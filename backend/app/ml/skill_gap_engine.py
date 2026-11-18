"""Explainable Weighted Skill Gap Engine powered by Exact, Synonym, and Semantic Matching."""

from typing import Any, Dict, List, Optional, Sequence

from app.ml.semantic_matcher import (
    CANONICAL_CATEGORY_MAP,
    compute_document_similarity,
    get_active_semantic_model_name,
    match_target_skill,
    normalize_skill_name,
)


def _dedupe_candidate_skills(skills: Sequence[str]) -> List[str]:
    seen = set()
    cleaned: List[str] = []
    for s in skills:
        val = (s or "").strip()
        if not val:
            continue
        key = val.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(val)
    return cleaned


def run_skill_gap_engine(
    candidate_skills: Sequence[str],
    required_skills: Sequence[Dict[str, Any]],
    preferred_skills: Sequence[Dict[str, Any]] = (),
    resume_text: Optional[str] = None,
    jd_text: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare verified candidate skills against job required & preferred skills with explainable weighted scoring."""
    deduped_candidates = _dedupe_candidate_skills(candidate_skills)
    used_candidate_keys: set[str] = set()

    # --- 1. Evaluate Required Skills ---
    matched_required: List[Dict[str, Any]] = []
    missing_required: List[Dict[str, Any]] = []
    total_required_weight = 0.0
    matched_required_weight = 0.0

    for req in required_skills:
        req_name = req["name"]
        req_category = req.get("category") or CANONICAL_CATEGORY_MAP.get(req_name.lower(), "General")
        weight = float(req.get("weight", 1.0))
        priority = req.get("priority") or ("Critical" if weight >= 1.3 else "Required")
        total_required_weight += weight

        outcome = match_target_skill(req_name, deduped_candidates)
        if outcome.matched:
            matched_required_weight += weight
            if outcome.matched_with:
                used_candidate_keys.add(outcome.matched_with.lower())
                used_candidate_keys.add(normalize_skill_name(outcome.matched_with).lower())
            matched_required.append(
                {
                    "skill": req_name,
                    "category": req_category,
                    "weight": round(weight, 2),
                    "priority": priority,
                    "match_type": outcome.match_type,
                    "matched_with": outcome.matched_with,
                    "similarity": round(outcome.similarity, 4),
                }
            )
        else:
            missing_required.append(
                {
                    "skill": req_name,
                    "category": req_category,
                    "weight": round(weight, 2),
                    "priority": priority,
                    "closest_candidate_skill": outcome.closest_candidate,
                    "closest_similarity": round(outcome.closest_similarity, 4),
                }
            )

    # Exact required formula: Matched Required Skill Weights / Total Required Skill Weights * 100
    compatibility_score = (
        round((matched_required_weight / total_required_weight) * 100.0, 2)
        if total_required_weight > 0
        else 0.0
    )

    # --- 2. Evaluate Preferred Skills Separately ---
    matched_preferred: List[Dict[str, Any]] = []
    missing_preferred: List[Dict[str, Any]] = []
    total_preferred_weight = 0.0
    matched_preferred_weight = 0.0

    for pref in preferred_skills:
        pref_name = pref["name"]
        pref_category = pref.get("category") or CANONICAL_CATEGORY_MAP.get(pref_name.lower(), "General")
        weight = float(pref.get("weight", 0.7))
        total_preferred_weight += weight

        outcome = match_target_skill(pref_name, deduped_candidates)
        if outcome.matched:
            matched_preferred_weight += weight
            if outcome.matched_with:
                used_candidate_keys.add(outcome.matched_with.lower())
                used_candidate_keys.add(normalize_skill_name(outcome.matched_with).lower())
            matched_preferred.append(
                {
                    "skill": pref_name,
                    "category": pref_category,
                    "weight": round(weight, 2),
                    "priority": "Preferred",
                    "match_type": outcome.match_type,
                    "matched_with": outcome.matched_with,
                    "similarity": round(outcome.similarity, 4),
                }
            )
        else:
            missing_preferred.append(
                {
                    "skill": pref_name,
                    "category": pref_category,
                    "weight": round(weight, 2),
                    "priority": "Preferred",
                    "closest_candidate_skill": outcome.closest_candidate,
                    "closest_similarity": round(outcome.closest_similarity, 4),
                }
            )

    preferred_score = (
        round((matched_preferred_weight / total_preferred_weight) * 100.0, 2)
        if total_preferred_weight > 0
        else None
    )

    # --- 3. Identify Additional (Bonus) Candidate Skills ---
    additional_skills: List[Dict[str, str]] = []
    for cand in deduped_candidates:
        cand_norm = normalize_skill_name(cand)
        if cand.lower() in used_candidate_keys or cand_norm.lower() in used_candidate_keys:
            continue
        additional_skills.append(
            {
                "skill": cand_norm,
                "original_name": cand,
                "category": CANONICAL_CATEGORY_MAP.get(cand_norm.lower(), "General"),
            }
        )

    # --- 4. Domain Breakdown for Skill Gap Bar Chart & Radar Chart ---
    all_categories = sorted(
        {
            *(item["category"] for item in matched_required),
            *(item["category"] for item in missing_required),
            *(item["category"] for item in matched_preferred),
            *(item["category"] for item in missing_preferred),
        }
    )

    category_breakdown: List[Dict[str, Any]] = []
    radar_data: List[Dict[str, Any]] = []

    for cat in all_categories:
        m_req = [i for i in matched_required if i["category"] == cat]
        x_req = [i for i in missing_required if i["category"] == cat]
        m_pref = [i for i in matched_preferred if i["category"] == cat]
        x_pref = [i for i in missing_preferred if i["category"] == cat]

        req_total_w = sum(i["weight"] for i in m_req) + sum(i["weight"] for i in x_req)
        req_match_w = sum(i["weight"] for i in m_req)
        domain_pct = round((req_match_w / req_total_w) * 100.0, 1) if req_total_w > 0 else (
            100.0 if m_pref and not x_pref else 0.0
        )

        category_breakdown.append(
            {
                "category": cat,
                "matched_required": len(m_req),
                "missing_required": len(x_req),
                "matched_preferred": len(m_pref),
                "missing_preferred": len(x_pref),
                "coverage_percent": domain_pct,
            }
        )
        radar_data.append(
            {
                "domain": cat,
                "candidate": domain_pct,
                "required": 100.0,
            }
        )

    # --- 5. Document-Level Semantic Similarity ---
    jd_semantic_similarity = (
        compute_document_similarity(resume_text, jd_text)
        if resume_text and jd_text
        else compute_document_similarity(
            ", ".join(deduped_candidates),
            ", ".join(r["name"] for r in required_skills),
        )
    )

    semantic_model = get_active_semantic_model_name()

    pref_clause = (
        f" Preferred skills calculated separately: {len(matched_preferred)} of "
        f"{len(preferred_skills)} matched (weight {matched_preferred_weight:.2f} / "
        f"{total_preferred_weight:.2f} = {preferred_score:.2f}%)."
        if preferred_score is not None
        else " No separate preferred skills were listed in this job description."
    )

    summary_text = (
        f"Matched {len(matched_required)} of {len(required_skills)} required skills "
        f"(matched weight {matched_required_weight:.2f} / total required weight "
        f"{total_required_weight:.2f} = {compatibility_score:.2f}%).{pref_clause}"
    )

    return {
        "compatibility_score": compatibility_score,
        "preferred_score": preferred_score,
        "jd_semantic_similarity": jd_semantic_similarity,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "additional_skills": additional_skills,
        "category_breakdown": category_breakdown,
        "radar_data": radar_data,
        "score_explanation": {
            "formula": "Matched Required Skill Weights / Total Required Skill Weights × 100",
            "matched_required_weight": round(matched_required_weight, 2),
            "total_required_weight": round(total_required_weight, 2),
            "compatibility_score": compatibility_score,
            "matched_preferred_weight": round(matched_preferred_weight, 2),
            "total_preferred_weight": round(total_preferred_weight, 2),
            "preferred_score": preferred_score,
            "jd_semantic_similarity": jd_semantic_similarity,
            "semantic_model": semantic_model,
            "summary_text": summary_text,
        },
    }
