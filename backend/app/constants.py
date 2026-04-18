"""
Single source of truth for shared constants used across services.
Eliminates duplicate definitions in parser.py, ats_scorer.py, etc.
"""

# ── Action verbs used in formatting checks and ATS scoring ──────────────────
ACTION_VERBS = [
    "developed", "built", "architected", "deployed", "optimized", "implemented",
    "automated", "scaled", "refactored", "migrated", "launched", "delivered",
    "designed", "managed", "led", "created", "achieved", "improved", "reduced",
    "increased", "streamlined", "collaborated", "negotiated", "generated",
    "spearheaded", "facilitated", "analyzed", "researched", "drafted",
    "recruited", "closed", "grew", "drove", "shipped", "executed", "trained",
    "coordinated", "maintained", "resolved", "established", "mentored",
    "oversaw", "audited", "modeled",
]

# ── ATS scoring weights ─────────────────────────────────────────────────────
ATS_WEIGHTS = {
    "keyword":    0.35,
    "formatting": 0.20,
    "section":    0.20,
    "experience": 0.15,
    "skill":      0.10,
}

# ── Grade thresholds ─────────────────────────────────────────────────────────
GRADE_THRESHOLDS = {"A": 80, "B": 65, "C": 50, "D": 35, "F": 0}

def get_grade(score: float) -> str:
    """Return letter grade for a given numeric score."""
    for grade, threshold in GRADE_THRESHOLDS.items():
        if score >= threshold:
            return grade
    return "F"

# ── Experience level thresholds ──────────────────────────────────────────────
def determine_level(years: float) -> str:
    if years < 1:
        return "fresher"
    elif years < 4:
        return "junior"
    elif years < 9:
        return "mid"
    else:
        return "senior"

# ── File validation magic bytes ──────────────────────────────────────────────
PDF_MAGIC = b'%PDF'
DOCX_MAGIC = b'PK\x03\x04'

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
