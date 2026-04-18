"""
Semantic Matcher — uses sentence-transformers for meaning-based JD matching.
Falls back gracefully if the model isn't installed.

Model: all-MiniLM-L6-v2 (80MB, runs on CPU in <1s)
Cost: $0 (runs locally)
"""
import numpy as np
from typing import Optional, Tuple

_MODEL = None
_MODEL_LOADED = False


def _load_model():
    """Lazy-load the sentence-transformer model (one-time, ~2s on first call)."""
    global _MODEL, _MODEL_LOADED
    if _MODEL_LOADED:
        return _MODEL
    try:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    except (ImportError, Exception):
        _MODEL = None
    _MODEL_LOADED = True
    return _MODEL


def is_available() -> bool:
    """Check if semantic matching is available."""
    return _load_model() is not None


def semantic_similarity(text_a: str, text_b: str) -> Optional[float]:
    """
    Compute cosine similarity between two texts using sentence embeddings.
    Returns float 0-1 or None if model unavailable.
    """
    model = _load_model()
    if model is None:
        return None

    # Truncate for speed — first 2000 chars capture the essence
    embeddings = model.encode([text_a[:2000], text_b[:2000]])
    cos_sim = float(np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]) + 1e-8
    ))
    return round(cos_sim, 4)


def enhanced_jd_match(
    resume_text: str,
    jd_text: str,
    tfidf_score: float,
) -> Tuple[float, str]:
    """
    Blend semantic similarity with TF-IDF for a more accurate match.
    Returns (blended_score_0_to_1, method_used).
    """
    sem_score = semantic_similarity(resume_text, jd_text)

    if sem_score is not None:
        # Blend: 60% semantic + 40% TF-IDF (semantic is more accurate)
        blended = 0.60 * sem_score + 0.40 * tfidf_score
        return round(blended, 4), "semantic+tfidf"
    else:
        return tfidf_score, "tfidf_only"
