"""
Semantic Matcher — hybrid JD matching with TF-IDF + optional AI embeddings.

Production behavior:
  - Uses TF-IDF (scikit-learn) as the primary matching engine — fast, reliable, zero extra deps.
  - Optionally blends in sentence-transformer embeddings when available for higher accuracy.
  - Falls back gracefully if sentence-transformers is not installed.

Model (when available): all-MiniLM-L6-v2 (80MB, runs on CPU in <1s, $0 cost)
"""
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

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
        logger.info("Sentence-transformer model loaded successfully")
    except ImportError:
        logger.info("sentence-transformers not installed — using TF-IDF only (this is normal for free-tier deployments)")
        _MODEL = None
    except Exception as e:
        logger.warning("Failed to load sentence-transformer model: %s", str(e))
        _MODEL = None
    _MODEL_LOADED = True
    return _MODEL


def is_available() -> bool:
    """Check if semantic (embedding-based) matching is available."""
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

    method_used will be:
      - "semantic+tfidf" when sentence-transformers is available
      - "tfidf" when using TF-IDF only (default on free-tier)
    """
    sem_score = semantic_similarity(resume_text, jd_text)

    if sem_score is not None:
        # Blend: 60% semantic + 40% TF-IDF (semantic is more accurate)
        blended = 0.60 * sem_score + 0.40 * tfidf_score
        logger.debug("JD match: semantic=%.4f tfidf=%.4f blended=%.4f", sem_score, tfidf_score, blended)
        return round(blended, 4), "semantic+tfidf"
    else:
        return tfidf_score, "tfidf"
