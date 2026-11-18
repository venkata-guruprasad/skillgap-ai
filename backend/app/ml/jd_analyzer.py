"""Job Description Analyzer: extracts required/preferred skills, soft skills, experience, education, and responsibilities."""

import re
from typing import Any, Dict, List

from app.ml.skill_extractor import extract_skills_from_sections
from app.ml.skill_taxonomy import (
    SOFT_SKILL_DEFINITIONS,
    TECHNICAL_SKILL_DEFINITIONS,
)
from app.ml.text_cleaner import clean_resume_text

JD_SECTION_HEADERS: Dict[str, List[str]] = {
    "responsibilities": [
        "responsibilities",
        "key responsibilities",
        "what you will do",
        "what you'll do",
        "role overview",
        "job responsibilities",
        "duties",
        "the role",
    ],
    "required": [
        "requirements",
        "required qualifications",
        "required skills",
        "must have",
        "must-have",
        "minimum qualifications",
        "basic qualifications",
        "what you bring",
        "qualifications",
        "technical requirements",
    ],
    "preferred": [
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "bonus",
        "bonus points",
        "plus",
        "good to have",
        "desired skills",
        "preferred",
    ],
}

EXPERIENCE_LINE_PATTERN = re.compile(
    r"(?:\b\d+\s*\+?\s*(?:to|-|–)?\s*\d*\s*years?\b|\bentry[- ]level\b|\bnew grad\b|\binternship\b|\bsenior[- ]level\b|\bmid[- ]level\b|\bexperience\s+(?:with|in|building|developing)\b)",
    re.IGNORECASE,
)

EDUCATION_LINE_PATTERN = re.compile(
    r"\b(?:bachelor(?:'s)?|master(?:'s)?|ph\.?d\.?|b\.?s\.?|m\.?s\.?|b\.?tech|m\.?tech|degree\s+in|computer\s+science|data\s+science|equivalent\s+practical\s+experience)\b",
    re.IGNORECASE,
)

CORE_PRIORITY_INDICATORS = re.compile(
    r"\b(?:strong|proficient|expert|deep|solid|required|must|mandatory|core|hands-on|production)\b",
    re.IGNORECASE,
)


def segment_jd_sections(cleaned_text: str) -> Dict[str, str]:
    """Segment a job description into general, responsibilities, required, and preferred sections."""
    buckets: Dict[str, List[str]] = {"general": []}
    current = "general"

    lookup: Dict[str, str] = {}
    for canonical, aliases in JD_SECTION_HEADERS.items():
        for alias in aliases:
            lookup[alias.lower()] = canonical

    for raw_line in cleaned_text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        norm_heading = re.sub(r"[:\-_|]+$", "", line).strip().lower()
        if norm_heading in lookup and len(line) <= 60:
            current = lookup[norm_heading]
            buckets.setdefault(current, [])
            continue

        # Handle inline section prefixes like "Preferred Skills: Docker, Kubernetes"
        inline_matched = False
        if ":" in line[:36]:
            prefix, rest = line.split(":", 1)
            pnorm = prefix.strip().lower()
            if pnorm in lookup:
                current = lookup[pnorm]
                buckets.setdefault(current, [])
                if rest.strip():
                    buckets[current].append(f"{prefix.strip()}: {rest.strip()}")
                inline_matched = True
        if inline_matched:
            continue

        buckets.setdefault(current, []).append(line)

    return {
        k: "\n".join(lines).strip()
        for k, lines in buckets.items()
        if "\n".join(lines).strip()
    }


def _compute_required_weight(
    skill_name: str,
    evidence: List[str],
    responsibilities_text: str,
) -> float:
    """Assign transparent importance weight (1.0 - 1.5) to a required skill."""
    weight = 1.0
    combined_ev = " ".join(evidence)
    if CORE_PRIORITY_INDICATORS.search(combined_ev):
        weight += 0.3
    if responsibilities_text and re.search(
        rf"(?<![A-Za-z0-9_]){re.escape(skill_name)}(?![A-Za-z0-9_+#])",
        responsibilities_text,
        re.IGNORECASE,
    ):
        weight += 0.2
    return round(min(1.5, weight), 2)


def _extract_experience_requirements(cleaned_text: str) -> List[str]:
    results: List[str] = []
    for raw_line in cleaned_text.split("\n"):
        line = raw_line.lstrip("- ").strip()
        if len(line) < 12:
            continue
        if EXPERIENCE_LINE_PATTERN.search(line) and line not in results:
            results.append(line[:240])
            if len(results) >= 6:
                break
    return results


def _extract_education_requirements(cleaned_text: str) -> List[str]:
    results: List[str] = []
    for raw_line in cleaned_text.split("\n"):
        line = raw_line.lstrip("- ").strip()
        if len(line) < 12:
            continue
        if EDUCATION_LINE_PATTERN.search(line) and line not in results:
            results.append(line[:240])
            if len(results) >= 4:
                break
    return results


def _extract_responsibilities(sections: Dict[str, str]) -> List[str]:
    resp_text = sections.get("responsibilities", "")
    results: List[str] = []
    if resp_text:
        for raw_line in resp_text.split("\n"):
            line = raw_line.lstrip("- ").strip()
            if len(line) >= 15 and line not in results:
                results.append(line[:260])
                if len(results) >= 8:
                    break
    return results


def analyze_job_description(raw_text: str) -> Dict[str, Any]:
    """Extract required skills, preferred skills, soft skills, experience, education, and responsibilities."""
    cleaned = clean_resume_text(raw_text)
    sections = segment_jd_sections(cleaned)

    required_text_parts = [
        sections.get("required", ""),
        sections.get("responsibilities", ""),
        sections.get("general", ""),
    ]
    required_section_map = {"skills": "\n".join(p for p in required_text_parts if p)}
    preferred_text = sections.get("preferred", "")
    preferred_section_map = {"skills": preferred_text} if preferred_text else {}

    req_confirmed, _ = extract_skills_from_sections(
        sections=required_section_map,
        definitions=TECHNICAL_SKILL_DEFINITIONS,
        full_text=cleaned,
    )
    pref_confirmed, _ = (
        extract_skills_from_sections(
            sections=preferred_section_map,
            definitions=TECHNICAL_SKILL_DEFINITIONS,
            full_text=cleaned,
        )
        if preferred_section_map
        else ([], [])
    )

    soft_confirmed, _ = extract_skills_from_sections(
        sections={"experience": cleaned},
        definitions=SOFT_SKILL_DEFINITIONS,
        full_text=cleaned,
    )

    responsibilities_text = sections.get("responsibilities", "")
    required_names_lower = {s.name.lower() for s in req_confirmed}

    required_skills: List[Dict[str, Any]] = []
    for skill in req_confirmed:
        weight = _compute_required_weight(skill.name, skill.evidence, responsibilities_text)
        priority = "Critical" if weight >= 1.3 else "Required"
        required_skills.append(
            {
                "name": skill.name,
                "category": skill.category,
                "weight": weight,
                "priority": priority,
                "evidence": skill.evidence[:2],
            }
        )

    # Preferred skills exclude any skill already listed as required
    preferred_skills: List[Dict[str, Any]] = []
    for skill in pref_confirmed:
        if skill.name.lower() in required_names_lower:
            continue
        preferred_skills.append(
            {
                "name": skill.name,
                "category": skill.category,
                "weight": 0.7,
                "priority": "Preferred",
                "evidence": skill.evidence[:2],
            }
        )

    required_skills.sort(key=lambda s: (-s["weight"], s["name"]))
    preferred_skills.sort(key=lambda s: s["name"])

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "soft_skills": [s.to_dict() for s in soft_confirmed],
        "experience_requirements": _extract_experience_requirements(cleaned),
        "education_requirements": _extract_education_requirements(cleaned),
        "responsibilities": _extract_responsibilities(sections),
        "summary": {
            "required_skill_count": len(required_skills),
            "preferred_skill_count": len(preferred_skills),
            "soft_skill_count": len(soft_confirmed),
            "total_required_weight": round(sum(s["weight"] for s in required_skills), 2),
            "total_preferred_weight": round(sum(s["weight"] for s in preferred_skills), 2),
            "word_count": len(cleaned.split()),
        },
    }
