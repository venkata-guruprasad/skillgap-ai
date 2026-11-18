"""Semantic skill & document matcher using sentence-transformers/all-MiniLM-L6-v2."""

from dataclasses import dataclass
from functools import lru_cache
import logging
import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from app.ml.skill_taxonomy import SYNONYM_MAP, TECHNICAL_SKILL_DEFINITIONS

logger = logging.getLogger("skillgap_ai.semantic_matcher")

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SEMANTIC_SKILL_MATCH_THRESHOLD = 0.68

# Canonical taxonomy skill set (lowercase) -> category
CANONICAL_CATEGORY_MAP: Dict[str, str] = {
    d.canonical.lower(): d.category for d in TECHNICAL_SKILL_DEFINITIONS
}

# Explicit distinct-skill pairs that must NEVER be equated semantically
# (prevents treating sibling/distinct technologies like Java vs JavaScript or AWS vs Azure as equivalent)
CANONICAL_NAMES_LOWER = set(CANONICAL_CATEGORY_MAP.keys())


@dataclass
class SkillMatchOutcome:
    matched: bool
    match_type: str  # "exact" | "synonym" | "semantic" | "none"
    matched_with: Optional[str]
    similarity: float
    closest_candidate: Optional[str] = None
    closest_similarity: float = 0.0


@lru_cache(maxsize=1)
def load_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    """Lazily load and cache SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')."""
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading SentenceTransformer model: %s", model_name)
        model = SentenceTransformer(model_name)
        return model, model_name
    except Exception as exc:
        logger.warning(
            "SentenceTransformer unavailable (%s); falling back to TF-IDF cosine similarity.",
            exc,
        )
        return None, "tfidf-fallback"


@lru_cache(maxsize=512)
def _embed_single_text(text: str) -> Optional[Tuple[float, ...]]:
    model, _ = load_embedding_model()
    if model is None:
        return None
    vec = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
    return tuple(float(x) for x in vec)


def _cosine_from_tuples(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return max(0.0, min(1.0, float(dot)))


def _tfidf_cosine_fallback(text_a: str, text_b: str) -> float:
    """Lightweight deterministic fallback if SentenceTransformer cannot be loaded."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vec = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        mat = vec.fit_transform([text_a, text_b])
        sim = float(cosine_similarity(mat[0:1], mat[1:2])[0][0])
        return max(0.0, min(1.0, sim))
    except Exception:
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())
        if not tokens_a or not tokens_b:
            return 0.0
        return len(tokens_a & tokens_b) / math.sqrt(len(tokens_a) * len(tokens_b))


def get_active_semantic_model_name() -> str:
    _, name = load_embedding_model()
    return name


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill string using our canonical synonym map when recognized."""
    cleaned = skill.strip()
    if not cleaned:
        return ""
    return SYNONYM_MAP.get(cleaned.lower(), cleaned)


def compute_text_similarity(text_a: str, text_b: str) -> float:
    """Compute semantic cosine similarity (0.0 - 1.0) between two texts."""
    a = (text_a or "").strip()
    b = (text_b or "").strip()
    if not a or not b:
        return 0.0
    if a.lower() == b.lower():
        return 1.0

    emb_a = _embed_single_text(a)
    emb_b = _embed_single_text(b)
    if emb_a is not None and emb_b is not None:
        return _cosine_from_tuples(emb_a, emb_b)
    return _tfidf_cosine_fallback(a, b)


def _are_distinct_canonical_skills(norm_target: str, norm_candidate: str) -> bool:
    """Prevent treating two distinct canonical taxonomy skills as equivalent (e.g., AWS != Azure, Java != JavaScript)."""
    t = norm_target.lower()
    c = norm_candidate.lower()
    if t == c:
        return False
    return t in CANONICAL_NAMES_LOWER and c in CANONICAL_NAMES_LOWER


def match_target_skill(
    target_skill: str,
    candidate_skills: Sequence[str],
    semantic_threshold: float = SEMANTIC_SKILL_MATCH_THRESHOLD,
) -> SkillMatchOutcome:
    """Match a required/preferred job skill against candidate skills using exact, synonym, and guarded semantic similarity."""
    if not candidate_skills:
        return SkillMatchOutcome(
            matched=False,
            match_type="none",
            matched_with=None,
            similarity=0.0,
        )

    target_clean = target_skill.strip()
    target_norm = normalize_skill_name(target_clean)

    # 1. Exact string match (case-insensitive)
    for cand in candidate_skills:
        if cand.strip().lower() == target_clean.lower():
            return SkillMatchOutcome(
                matched=True,
                match_type="exact",
                matched_with=cand.strip(),
                similarity=1.0,
                closest_candidate=cand.strip(),
                closest_similarity=1.0,
            )

    # 2. Synonym / canonical taxonomy normalization match (e.g., ML == Machine Learning, JS == JavaScript)
    for cand in candidate_skills:
        cand_norm = normalize_skill_name(cand)
        if cand_norm.lower() == target_norm.lower():
            return SkillMatchOutcome(
                matched=True,
                match_type="synonym",
                matched_with=cand.strip(),
                similarity=1.0,
                closest_candidate=cand.strip(),
                closest_similarity=1.0,
            )

    # 3. Guarded semantic similarity via Sentence Transformers (all-MiniLM-L6-v2)
    best_cand: Optional[str] = None
    best_sim = 0.0
    best_valid_cand: Optional[str] = None
    best_valid_sim = 0.0

    for cand in candidate_skills:
        cand_clean = cand.strip()
        cand_norm = normalize_skill_name(cand_clean)
        sim = compute_text_similarity(target_norm, cand_norm)

        if sim > best_sim:
            best_sim = sim
            best_cand = cand_clean

        # Do NOT equate two distinct canonical technologies (e.g., TensorFlow vs PyTorch, Java vs JavaScript)
        if _are_distinct_canonical_skills(target_norm, cand_norm):
            continue

        if sim > best_valid_sim:
            best_valid_sim = sim
            best_valid_cand = cand_clean

    if best_valid_cand is not None and best_valid_sim >= semantic_threshold:
        return SkillMatchOutcome(
            matched=True,
            match_type="semantic",
            matched_with=best_valid_cand,
            similarity=round(best_valid_sim, 4),
            closest_candidate=best_valid_cand,
            closest_similarity=round(best_valid_sim, 4),
        )

    return SkillMatchOutcome(
        matched=False,
        match_type="none",
        matched_with=None,
        similarity=0.0,
        closest_candidate=best_cand,
        closest_similarity=round(best_sim, 4),
    )


def compute_document_similarity(resume_text: str, jd_text: str) -> float:
    """Compute overall Resume-to-JD semantic similarity as a percentage (0.0 - 100.0)."""
    if not resume_text or not jd_text:
        return 0.0
    # Truncate gracefully to keep MiniLM token window focused on highest-signal content
    sim = compute_text_similarity(resume_text[:3000], jd_text[:3000])
    return round(sim * 100.0, 2)
