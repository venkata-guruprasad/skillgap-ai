"""Context-aware NLP skill extractor powered by spaCy, NLTK, and evidence verification."""

from dataclasses import dataclass, field
from functools import lru_cache
import re
from typing import Dict, List, Optional, Sequence, Tuple

import nltk
import spacy

from app.ml.skill_taxonomy import (
    SOFT_SKILL_DEFINITIONS,
    TECHNICAL_SKILL_DEFINITIONS,
    SkillDefinition,
)
from app.ml.text_cleaner import redact_pii

# Section weighting reflects how strongly a mention signals an actual candidate skill
SECTION_CONFIDENCE_BONUS: Dict[str, float] = {
    "skills": 0.35,
    "projects": 0.25,
    "experience": 0.25,
    "certifications": 0.25,
    "summary": 0.15,
    "education": 0.12,
    "general": 0.05,
}

CONFIRMATION_THRESHOLD = 0.65


@dataclass
class ExtractedSkillMatch:
    name: str
    category: str
    confidence: float
    confirmed: bool
    matched_terms: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "category": self.category,
            "confidence": round(self.confidence, 2),
            "confirmed": self.confirmed,
            "matched_terms": self.matched_terms,
            "sections": self.sections,
            "evidence": self.evidence,
            "reason": self.reason,
        }


@lru_cache(maxsize=1)
def get_spacy_nlp():
    """Load spaCy English model if available, else configure spaCy blank English pipeline."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp


def tokenize_sentences_nltk_or_spacy(text: str) -> List[str]:
    """Split text into sentences using NLTK punkt when available, with spaCy fallback."""
    if not text:
        return []
    try:
        sentences = nltk.sent_tokenize(text)
        if sentences:
            return [s.strip() for s in sentences if s.strip()]
    except LookupError:
        pass
    nlp = get_spacy_nlp()
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def build_alias_regex(alias: str) -> re.Pattern[str]:
    """Compile a boundary-safe regex supporting tokens with symbols (C++, C#, Node.js)."""
    escaped = re.escape(alias)
    # Use negative lookbehind/lookahead on word characters so C++ and Node.js match cleanly
    return re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_+#])", re.IGNORECASE)


def _extract_snippet(line: str, start: int, end: int, radius: int = 65) -> str:
    left = max(0, start - radius)
    right = min(len(line), end + radius)
    snippet = line[left:right].strip()
    if left > 0:
        snippet = "..." + snippet
    if right < len(line):
        snippet = snippet + "..."
    return redact_pii(snippet)


def _has_negative_context(line: str, definition: SkillDefinition) -> bool:
    for neg in definition.negative_patterns:
        if re.search(neg, line, re.IGNORECASE):
            return True
    return False


def _count_context_hits(text_window: str, definition: SkillDefinition) -> int:
    lower = text_window.lower()
    hits = 0
    for kw in definition.context_keywords:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(kw)}(?![A-Za-z0-9_])", lower):
            hits += 1
    return hits


def _is_skill_list_line(line: str) -> bool:
    """Detect structured skill listing lines (e.g., 'Skills: Python, JS, Docker, AWS')."""
    comma_or_pipe_count = line.count(",") + line.count("|") + line.count("/")
    return comma_or_pipe_count >= 2 or ":" in line[:30]


def extract_skills_from_sections(
    sections: Dict[str, str],
    definitions: Sequence[SkillDefinition],
    full_text: str,
) -> Tuple[List[ExtractedSkillMatch], List[ExtractedSkillMatch]]:
    """Extract skills with synonym normalization, evidence snippets, and anti-false-positive gating."""
    confirmed: List[ExtractedSkillMatch] = []
    unconfirmed: List[ExtractedSkillMatch] = []

    full_text_lower = full_text.lower()

    for definition in definitions:
        matched_terms: List[str] = []
        matched_sections: List[str] = []
        evidence_snippets: List[str] = []
        best_confidence = 0.0
        rejected_by_negative = False

        aliases_to_check = list(dict.fromkeys([definition.canonical, *definition.aliases]))
        compiled_aliases = [(alias, build_alias_regex(alias)) for alias in aliases_to_check]

        for section_name, section_text in sections.items():
            if not section_text:
                continue

            section_bonus = SECTION_CONFIDENCE_BONUS.get(section_name, 0.05)

            for raw_line in section_text.split("\n"):
                stripped_line = raw_line.strip()
                if not stripped_line:
                    continue

                # Use NLTK/spaCy sentence tokenization for multi-sentence lines to produce focused evidence snippets
                candidate_units = (
                    tokenize_sentences_nltk_or_spacy(stripped_line)
                    if len(stripped_line) > 120
                    else [stripped_line]
                )

                for line in candidate_units:
                    for alias, pattern in compiled_aliases:
                        for match in pattern.finditer(line):
                            matched_surface = match.group(0)
                            is_ambiguous = alias in definition.ambiguous_aliases or len(alias) <= 2

                            # Guard 1: explicit negative idiom/unit context near this specific match
                            local_neg_window = line[
                                max(0, match.start() - 20) : min(len(line), match.end() + 26)
                            ]
                            if _has_negative_context(local_neg_window, definition):
                                rejected_by_negative = True
                                continue

                            # Guard 2: single-letter or ultra-short ambiguous token ('R', 'JS', 'ML', 'TF', 'Go')
                            # requires either explicit skill-section/list context OR technical co-occurrence
                            local_context_hits = _count_context_hits(line, definition)
                            global_context_hits = _count_context_hits(full_text_lower, definition)
                            is_list_line = _is_skill_list_line(line)

                            if is_ambiguous:
                                # Case-sensitivity hint for short acronyms like ML, JS, NLP, TF, R
                                if len(alias) <= 3 and matched_surface.islower():
                                    # lowercase 'ml', 'r', 'go', 'tf' in narrative prose is usually noise
                                    if section_name != "skills" and not is_list_line:
                                        continue

                                if section_name == "skills":
                                    base_score = 0.56
                                elif is_list_line and local_context_hits >= 1:
                                    base_score = 0.54
                                elif local_context_hits >= 2:
                                    base_score = 0.52
                                elif local_context_hits == 1 and section_name in {"projects", "experience", "certifications"}:
                                    base_score = 0.48
                                else:
                                    # Weak isolated keyword match in unrelated prose -> keep below confirmation threshold
                                    base_score = 0.30
                            else:
                                base_score = 0.62

                            context_bonus = min(0.18, local_context_hits * 0.07 + min(global_context_hits, 2) * 0.03)
                            list_bonus = 0.08 if is_list_line else 0.0
                            score = min(0.99, base_score + section_bonus + context_bonus + list_bonus)

                            if score > best_confidence:
                                best_confidence = score

                            if matched_surface not in matched_terms:
                                matched_terms.append(matched_surface)
                            if section_name not in matched_sections:
                                matched_sections.append(section_name)

                            snippet = _extract_snippet(line, match.start(), match.end())
                            if snippet and snippet not in evidence_snippets and len(evidence_snippets) < 3:
                                evidence_snippets.append(snippet)

        if matched_terms:
            is_confirmed = best_confidence >= CONFIRMATION_THRESHOLD
            entry = ExtractedSkillMatch(
                name=definition.canonical,
                category=definition.category,
                confidence=best_confidence,
                confirmed=is_confirmed,
                matched_terms=matched_terms,
                sections=matched_sections,
                evidence=evidence_snippets,
                reason=None
                if is_confirmed
                else "Weak or ambiguous mention without sufficient technical context.",
            )
            if is_confirmed:
                confirmed.append(entry)
            else:
                unconfirmed.append(entry)
        elif rejected_by_negative:
            # Intentionally excluded false positives are not confirmed
            continue

    confirmed.sort(key=lambda item: (-item.confidence, item.name))
    unconfirmed.sort(key=lambda item: (-item.confidence, item.name))
    return confirmed, unconfirmed


def extract_all_skills(
    sections: Dict[str, str],
    full_text: str,
) -> Dict[str, object]:
    """Extract normalized technical and soft skills with evidence snippets."""
    tech_confirmed, tech_unconfirmed = extract_skills_from_sections(
        sections=sections,
        definitions=TECHNICAL_SKILL_DEFINITIONS,
        full_text=full_text,
    )
    soft_confirmed, _ = extract_skills_from_sections(
        sections=sections,
        definitions=SOFT_SKILL_DEFINITIONS,
        full_text=full_text,
    )

    by_category: Dict[str, List[Dict[str, object]]] = {}
    for skill in tech_confirmed:
        by_category.setdefault(skill.category, []).append(skill.to_dict())

    return {
        "technical_skills": [s.to_dict() for s in tech_confirmed],
        "soft_skills": [s.to_dict() for s in soft_confirmed],
        "unconfirmed_mentions": [s.to_dict() for s in tech_unconfirmed],
        "skills_by_category": by_category,
    }
