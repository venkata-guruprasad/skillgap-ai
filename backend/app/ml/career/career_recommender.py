"""Career recommendation module: combines trained TF-IDF classifier, MiniLM cosine similarity, and Skill Gap Engine."""

from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from app.ml.career.model_loader import load_trained_bundle
from app.ml.semantic_matcher import compute_text_similarity, load_embedding_model
from app.ml.skill_gap_engine import run_skill_gap_engine

EMPLOYMENT_DISCLAIMER = (
    "Compatibility scores reflect skill alignment, semantic profile similarity, and "
    "model classification confidence on our role taxonomy — they are NOT actual "
    "employment or hiring probabilities."
)


def _build_candidate_profile_text(
    resume_skills: Sequence[str],
    education: Sequence[str],
    experience: Sequence[str],
    projects: Sequence[str],
    career_interests: Sequence[str],
) -> str:
    parts: List[str] = []
    if resume_skills:
        parts.append(f"Technical skills: {', '.join(resume_skills)}.")
    if education:
        parts.append(f"Education: {' ; '.join(education)}.")
    if experience:
        parts.append(f"Experience: {' ; '.join(experience)}.")
    if projects:
        parts.append(f"Projects: {' ; '.join(projects)}.")
    if career_interests:
        parts.append(f"Career interests: {', '.join(career_interests)}.")
    return " ".join(parts).strip()


def _compute_interest_bonus(
    role: Dict[str, Any],
    career_interests: Sequence[str],
) -> float:
    if not career_interests:
        return 0.0
    role_tokens = {
        role["title"].lower(),
        role["category"].lower(),
        *(t.lower() for t in role.get("interest_tags", [])),
    }
    for interest in career_interests:
        val = (interest or "").strip().lower()
        if not val:
            continue
        if any(val in tok or tok in val for tok in role_tokens):
            return 6.0
    return 0.0


def predict_top_careers(
    resume_skills: Sequence[str],
    education: Sequence[str] = (),
    experience: Sequence[str] = (),
    projects: Sequence[str] = (),
    career_interests: Sequence[str] = (),
    top_k: int = 5,
    job_title_to_id: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """Return top-K career recommendations combining ML classifier, MiniLM cosine similarity, and Skill Gap Engine."""
    bundle = load_trained_bundle()
    pipeline = bundle["pipeline"]
    classes: List[str] = list(bundle["classes"])
    catalog: List[Dict[str, Any]] = bundle["role_catalog"]
    role_embeddings: Optional[Dict[str, List[float]]] = bundle.get("role_embeddings")

    clean_skills = [s.strip() for s in resume_skills if s and s.strip()]
    profile_text = _build_candidate_profile_text(
        resume_skills=clean_skills,
        education=education,
        experience=experience,
        projects=projects,
        career_interests=career_interests,
    )

    # 1. Trained Scikit-learn TF-IDF classifier probabilities across all 12 roles
    probs = pipeline.predict_proba([profile_text])[0]
    prob_by_role: Dict[str, float] = {
        cls_name: float(probs[idx]) for idx, cls_name in enumerate(classes)
    }

    # 2. Candidate MiniLM embedding for cosine similarity against precomputed role prototypes
    cand_vec = None
    model, active_semantic_model = load_embedding_model()
    if model is not None and role_embeddings:
        cand_vec = np.asarray(
            model.encode(profile_text[:3000], normalize_embeddings=True, show_progress_bar=False),
            dtype=np.float32,
        )

    scored_roles: List[Dict[str, Any]] = []
    job_lookup = {k.lower(): v for k, v in (job_title_to_id or {}).items()}

    for role in catalog:
        title = role["title"]
        required = role["required_skills"]
        preferred = role["preferred_skills"]

        # 3. Support every recommendation with the Skill Gap Engine
        gap = run_skill_gap_engine(
            candidate_skills=clean_skills,
            required_skills=required,
            preferred_skills=preferred,
        )
        skill_gap_score = float(gap["compatibility_score"])
        preferred_score = gap["preferred_score"]

        # Classifier score (scaled relative to top class & raw probability so probabilities are informative)
        raw_prob = prob_by_role.get(title, 0.0)
        max_prob = max(prob_by_role.values()) if prob_by_role else 1.0
        ml_classifier_score = round(
            min(100.0, (0.55 * raw_prob + 0.45 * (raw_prob / max(max_prob, 1e-6))) * 100.0),
            2,
        )

        # Semantic cosine similarity via Sentence Transformers (all-MiniLM-L6-v2)
        if cand_vec is not None and title in (role_embeddings or {}):
            proto_vec = np.asarray(role_embeddings[title], dtype=np.float32)
            sem_cos = float(np.clip(np.dot(cand_vec, proto_vec), 0.0, 1.0))
        else:
            sem_cos = compute_text_similarity(profile_text, role["role_description"])
        semantic_similarity = round(sem_cos * 100.0, 2)

        interest_bonus = _compute_interest_bonus(role, career_interests)

        # Hybrid transparent compatibility formula:
        # 55% weighted required skill match + 25% ML TF-IDF classifier + 20% MiniLM semantic similarity + interest bonus
        compatibility_score = round(
            min(
                100.0,
                0.55 * skill_gap_score
                + 0.25 * ml_classifier_score
                + 0.20 * semantic_similarity
                + interest_bonus,
            ),
            2,
        )

        matched_names = [s["skill"] for s in gap["matched_required_skills"]]
        missing_names = [s["skill"] for s in gap["missing_required_skills"]]
        missing_pref_names = [s["skill"] for s in gap["missing_preferred_skills"]]
        candidate_bonus_names = [s["skill"] for s in gap["additional_skills"]]

        # Required additional skills: missing required skills (ordered by weight) + top missing preferred
        required_additional = list(dict.fromkeys(missing_names + missing_pref_names[:3]))

        matched_clause = (
            f"Matches {len(matched_names)}/{len(required)} required skills "
            f"({', '.join(matched_names[:4])})"
            if matched_names
            else "Currently has limited direct overlap with core required skills"
        )
        missing_clause = (
            f"Adding {', '.join(missing_names[:3])} will most improve readiness."
            if missing_names
            else "Covers all core required skills for this track."
        )
        interest_clause = (
            " Boosted by your selected career interest." if interest_bonus > 0 else ""
        )

        explanation = (
            f"{matched_clause}. "
            f"Hybrid alignment: {skill_gap_score:.1f}% skill gap match, "
            f"{ml_classifier_score:.1f}% ML classifier alignment ({bundle['selected_model_name']}), "
            f"and {semantic_similarity:.1f}% semantic profile similarity ({active_semantic_model}). "
            f"{missing_clause}{interest_clause}"
        )

        scored_roles.append(
            {
                "career_title": title,
                "category": role["category"],
                "avg_salary": role["avg_salary"],
                "demand_level": role["demand_level"],
                "role_description": role["role_description"],
                "compatibility_score": compatibility_score,
                "score_breakdown": {
                    "skill_gap_score": skill_gap_score,
                    "preferred_skill_score": preferred_score,
                    "ml_classifier_score": ml_classifier_score,
                    "ml_raw_probability": round(raw_prob, 4),
                    "semantic_similarity": semantic_similarity,
                    "interest_bonus": interest_bonus,
                },
                "matching_skills": matched_names,
                "missing_skills": missing_names,
                "required_additional_skills": required_additional,
                "candidate_additional_skills": candidate_bonus_names[:8],
                "explanation": explanation,
                "linked_job_id": job_lookup.get(title.lower()),
            }
        )

    scored_roles.sort(
        key=lambda r: (
            -r["compatibility_score"],
            -r["score_breakdown"]["skill_gap_score"],
            r["career_title"],
        )
    )

    eval_report = bundle.get("evaluation_report", {})
    return {
        "top_recommendations": scored_roles[:top_k],
        "total_roles_evaluated": len(scored_roles),
        "disclaimer": EMPLOYMENT_DISCLAIMER,
        "model_metadata": {
            "selected_classifier": bundle.get("selected_model_name"),
            "semantic_model": active_semantic_model,
            "is_synthetic_dataset": bundle.get("is_synthetic_dataset", True),
            "dataset_provenance": bundle.get("dataset_provenance"),
            "trained_at": bundle.get("trained_at"),
            "evaluation_summary": {
                "accuracy": eval_report.get("accuracy"),
                "precision_macro": eval_report.get("precision_macro"),
                "recall_macro": eval_report.get("recall_macro"),
                "f1_macro": eval_report.get("f1_macro"),
                "test_samples": eval_report.get("test_samples"),
                "train_samples": eval_report.get("train_samples"),
                "evaluation_notice": eval_report.get("evaluation_notice"),
                "model_comparison": eval_report.get("model_comparison", []),
            },
        },
    }
