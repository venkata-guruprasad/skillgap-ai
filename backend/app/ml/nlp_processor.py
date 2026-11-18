"""Full NLP resume processing pipeline using spaCy, NLTK, and section segmentation."""

import re
from typing import Any, Dict, List, Optional

from app.ml.skill_extractor import extract_all_skills, get_spacy_nlp
from app.ml.text_cleaner import (
    EMAIL_REGEX,
    PHONE_REGEX,
    clean_resume_text,
    mask_email,
    mask_phone,
    redact_pii,
)

SECTION_HEADERS: Dict[str, List[str]] = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "about me",
        "career objective",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internships",
        "career history",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
        "selected projects",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
        "tools & technologies",
        "skills & technologies",
        "programming languages",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses & certifications",
        "courses & certifications",
        "achievements & certifications",
    ],
}

DEGREE_PATTERN = re.compile(
    r"\b(?:B\.?S\.?|B\.?Sc\.?|B\.?Tech\.?|B\.?E\.?|M\.?S\.?|M\.?Sc\.?|M\.?Tech\.?|M\.?B\.?A\.?|Ph\.?D\.?|"
    r"Bachelor(?:'s)?|Master(?:'s)?|Associate(?:'s)?|Diploma)\b",
    re.IGNORECASE,
)
YEAR_RANGE_PATTERN = re.compile(
    r"\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:19|20)\d{2}"
    r"(?:\s*(?:-|–|to)\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:(?:19|20)\d{2}|Present|Current))?\b",
    re.IGNORECASE,
)
CERT_PATTERN = re.compile(
    r"\b(?:AWS Certified|Microsoft Certified|Azure|Google Cloud|TensorFlow Developer|"
    r"Certified Kubernetes|CKA|CKAD|PMP|CompTIA|Cisco CCNA|Oracle Certified|"
    r"Coursera|DeepLearning\.AI|Databricks Certified|Scrum Master)\b",
    re.IGNORECASE,
)


def segment_resume_sections(cleaned_text: str) -> Dict[str, str]:
    """Segment a resume into normalized sections (summary, education, experience, projects, skills, certifications)."""
    sections: Dict[str, List[str]] = {"general": []}
    current_section = "general"

    header_lookup: Dict[str, str] = {}
    for canonical, aliases in SECTION_HEADERS.items():
        for alias in aliases:
            header_lookup[alias.lower()] = canonical

    for raw_line in cleaned_text.split("\n"):
        line = raw_line.strip()
        if not line:
            sections.setdefault(current_section, []).append("")
            continue

        normalized_heading = re.sub(r"[:\-_|]+$", "", line).strip().lower()
        if normalized_heading in header_lookup and len(line) <= 50:
            current_section = header_lookup[normalized_heading]
            sections.setdefault(current_section, [])
            continue

        # Also handle inline section prefix like "Technical Skills: Python, React, SQL"
        inline_matched = False
        if ":" in line[:32]:
            prefix, remainder = line.split(":", 1)
            prefix_norm = prefix.strip().lower()
            if prefix_norm in header_lookup:
                current_section = header_lookup[prefix_norm]
                sections.setdefault(current_section, [])
                if remainder.strip():
                    sections[current_section].append(f"{prefix.strip()}: {remainder.strip()}")
                inline_matched = True
        if inline_matched:
            continue

        sections.setdefault(current_section, []).append(line)

    return {
        key: "\n".join(lines).strip()
        for key, lines in sections.items()
        if "\n".join(lines).strip()
    }


def _extract_redacted_personal_info(cleaned_text: str) -> Dict[str, Any]:
    """Detect name, email, and phone using spaCy NER & regex, returning ONLY privacy-safe redacted summaries."""
    top_lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()][:6]
    top_block = "\n".join(top_lines)

    email_match = EMAIL_REGEX.search(cleaned_text)
    phone_match = PHONE_REGEX.search(cleaned_text)

    detected_name: Optional[str] = None
    nlp = get_spacy_nlp()
    if "ner" in nlp.pipe_names:
        doc = nlp(top_block)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
                detected_name = ent.text.strip()
                break

    # Heuristic fallback on line 1 when spaCy blank model is active
    if not detected_name and top_lines:
        first_line = top_lines[0].lstrip("- ").strip()
        words = first_line.split()
        if (
            2 <= len(words) <= 4
            and "@" not in first_line
            and not any(ch.isdigit() for ch in first_line)
            and first_line.lower() not in {"resume", "curriculum vitae", "cv"}
            and all(w[0].isupper() for w in words if w.isalpha())
        ):
            detected_name = first_line

    masked_name = None
    if detected_name:
        parts = detected_name.split()
        masked_name = f"{parts[0][0]}. {parts[-1][0]}." if len(parts) >= 2 else f"{parts[0][0]}."

    return {
        "name_detected": bool(detected_name),
        "masked_name": masked_name,
        "email_detected": bool(email_match),
        "masked_email": mask_email(email_match.group(0)) if email_match else None,
        "phone_detected": bool(phone_match),
        "masked_phone": mask_phone(phone_match.group(0)) if phone_match else None,
        "pii_redacted": True,
    }


def _extract_education(sections: Dict[str, str], cleaned_text: str) -> List[Dict[str, Optional[str]]]:
    edu_text = sections.get("education", "")
    entries: List[Dict[str, Optional[str]]] = []

    if edu_text:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", edu_text) if b.strip()]
        if len(blocks) == 1 and len(blocks[0].split("\n")) > 3:
            blocks = [line.strip() for line in blocks[0].split("\n") if line.strip()]

        for block in blocks[:6]:
            clean_block = redact_pii(block)
            lines = [ln.lstrip("- ").strip() for ln in clean_block.split("\n") if ln.strip()]
            if not lines:
                continue
            degree_line = next((ln for ln in lines if DEGREE_PATTERN.search(ln)), lines[0])
            year_match = YEAR_RANGE_PATTERN.search(clean_block)
            institution = next(
                (ln for ln in lines if ln != degree_line and any(k in ln.lower() for k in ("university", "institute", "college", "school", "academy"))),
                lines[1] if len(lines) > 1 else None,
            )
            entries.append(
                {
                    "degree": degree_line[:160],
                    "institution": institution[:160] if institution else None,
                    "period": year_match.group(0) if year_match else None,
                    "details": " | ".join(lines)[:280],
                }
            )
    else:
        # Fallback: scan cleaned text for explicit degree lines
        for line in cleaned_text.split("\n"):
            if DEGREE_PATTERN.search(line):
                year_match = YEAR_RANGE_PATTERN.search(line)
                entries.append(
                    {
                        "degree": redact_pii(line.lstrip("- ").strip())[:160],
                        "institution": None,
                        "period": year_match.group(0) if year_match else None,
                        "details": redact_pii(line.lstrip("- ").strip())[:240],
                    }
                )
                if len(entries) >= 3:
                    break

    return entries


def _extract_experience(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    exp_text = sections.get("experience", "")
    if not exp_text:
        return []

    entries: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    for raw_line in exp_text.split("\n"):
        line = redact_pii(raw_line.strip())
        if not line:
            continue

        is_bullet = line.startswith("- ")
        if not is_bullet:
            year_match = YEAR_RANGE_PATTERN.search(line)
            if current is None or year_match or "|" in line or " at " in line.lower() or len(current["highlights"]) > 0:
                if current is not None:
                    entries.append(current)
                title_part = line
                org_part = None
                if "|" in line:
                    pieces = [p.strip() for p in line.split("|") if p.strip()]
                    title_part = pieces[0]
                    org_part = pieces[1] if len(pieces) > 1 else None
                elif " - " in line and not (year_match and year_match.group(0) in line):
                    pieces = [p.strip() for p in line.split(" - ", 1)]
                    title_part, org_part = pieces[0], pieces[1]
                current = {
                    "role": title_part[:160],
                    "organization": org_part[:140] if org_part else None,
                    "duration": year_match.group(0) if year_match else None,
                    "highlights": [],
                }
            else:
                if not current["organization"]:
                    current["organization"] = line[:140]
                else:
                    current["highlights"].append(line[:240])
        else:
            highlight = line[2:].strip()
            if current is None:
                current = {
                    "role": "Work Experience Entry",
                    "organization": None,
                    "duration": None,
                    "highlights": [],
                }
            if highlight and len(current["highlights"]) < 5:
                current["highlights"].append(highlight[:240])

    if current is not None:
        entries.append(current)

    return entries[:8]


def _extract_projects(sections: Dict[str, str], confirmed_skill_names: List[str]) -> List[Dict[str, Any]]:
    proj_text = sections.get("projects", "")
    if not proj_text:
        return []

    entries: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    for raw_line in proj_text.split("\n"):
        line = redact_pii(raw_line.strip())
        if not line:
            continue

        if not line.startswith("- "):
            if current is not None:
                entries.append(current)
            title = line.split("|")[0].split("—")[0].strip()
            desc = line[len(title):].lstrip(" |:-").strip()
            current = {
                "title": title[:160],
                "description": desc[:300] if desc else "",
                "technologies": [],
            }
        else:
            bullet = line[2:].strip()
            if current is None:
                current = {"title": bullet[:120], "description": "", "technologies": []}
            else:
                current["description"] = (
                    f"{current['description']} {bullet}".strip()[:360]
                    if current["description"]
                    else bullet[:360]
                )

    if current is not None:
        entries.append(current)

    # Tag technologies mentioned in each project entry
    for entry in entries:
        combined = f"{entry['title']} {entry['description']}".lower()
        techs = [
            skill
            for skill in confirmed_skill_names
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(skill.lower())}(?![A-Za-z0-9_+#])", combined)
        ]
        entry["technologies"] = techs[:8]

    return entries[:8]


def _extract_certifications(sections: Dict[str, str], cleaned_text: str) -> List[str]:
    certs: List[str] = []
    cert_text = sections.get("certifications", "")

    if cert_text:
        for line in cert_text.split("\n"):
            cleaned = redact_pii(line.lstrip("- ").strip())
            if len(cleaned) >= 4 and cleaned not in certs:
                certs.append(cleaned[:180])
    else:
        for line in cleaned_text.split("\n"):
            if CERT_PATTERN.search(line):
                cleaned = redact_pii(line.lstrip("- ").strip())
                if cleaned not in certs:
                    certs.append(cleaned[:180])

    return certs[:10]


def _build_analysis_summary(
    cleaned_text: str,
    sections: Dict[str, str],
    education: List[Dict[str, Any]],
    experience: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    certifications: List[str],
    technical_skills: List[Dict[str, Any]],
    soft_skills: List[Dict[str, Any]],
) -> Dict[str, Any]:
    words = re.findall(r"\b\w+\b", cleaned_text)
    word_count = len(words)

    detected_sections = [
        name.title()
        for name in ("summary", "education", "experience", "projects", "skills", "certifications")
        if name in sections
    ]

    # Compute transparent content-grounded structure score (not a black-box ML model)
    score = 35
    if education:
        score += 12
    if experience:
        score += 15
    if projects:
        score += 12
    if len(technical_skills) >= 5:
        score += 14
    elif len(technical_skills) >= 2:
        score += 8
    if soft_skills:
        score += 6
    if certifications:
        score += 6
    ats_score = min(100, score)

    recommendations: List[str] = []
    if not experience:
        recommendations.append(
            "Add a clearly labeled Work Experience or Internships section with impact metrics."
        )
    if not projects:
        recommendations.append(
            "Include a Projects section demonstrating how you applied your technical skills."
        )
    if len(technical_skills) < 5:
        recommendations.append(
            "Expand your Technical Skills section with specific languages, frameworks, and tools used in your projects."
        )
    if not soft_skills:
        recommendations.append(
            "Highlight collaboration, leadership, or communication outcomes within your experience bullet points."
        )
    if not certifications:
        recommendations.append(
            "Consider listing relevant technical certifications or specialized coursework."
        )
    if word_count < 150:
        recommendations.append(
            "Your resume text is brief; consider adding concise, quantified achievements for each role or project."
        )
    if not recommendations:
        recommendations.append(
            "Strong resume structure with well-evidenced technical skills, projects, and experience."
        )

    return {
        "word_count": word_count,
        "ats_score": ats_score,
        "sections_detected": detected_sections,
        "technical_skill_count": len(technical_skills),
        "soft_skill_count": len(soft_skills),
        "education_count": len(education),
        "experience_count": len(experience),
        "project_count": len(projects),
        "certification_count": len(certifications),
        "recommendations": recommendations,
    }


def analyze_resume_text(raw_text: str) -> Dict[str, Any]:
    """Run full cleaning, section segmentation, NLP entity parsing, and skill extraction."""
    cleaned_text = clean_resume_text(raw_text)
    sections = segment_resume_sections(cleaned_text)

    personal_info = _extract_redacted_personal_info(cleaned_text)
    skills_result = extract_all_skills(sections=sections, full_text=cleaned_text)

    confirmed_tech_names = [s["name"] for s in skills_result["technical_skills"]]
    education = _extract_education(sections, cleaned_text)
    experience = _extract_experience(sections)
    projects = _extract_projects(sections, confirmed_tech_names)
    certifications = _extract_certifications(sections, cleaned_text)

    summary = _build_analysis_summary(
        cleaned_text=cleaned_text,
        sections=sections,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        technical_skills=skills_result["technical_skills"],
        soft_skills=skills_result["soft_skills"],
    )

    return {
        "cleaned_text_preview": redact_pii(cleaned_text[:600]),
        "personal_info": personal_info,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "technical_skills": skills_result["technical_skills"],
        "soft_skills": skills_result["soft_skills"],
        "unconfirmed_mentions": skills_result["unconfirmed_mentions"],
        "skills_by_category": skills_result["skills_by_category"],
        "summary": summary,
    }
