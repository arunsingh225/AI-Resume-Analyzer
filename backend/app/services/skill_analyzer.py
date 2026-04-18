"""
skill_analyzer.py — Robust ATS Skill Detection Engine

Features:
  - Synonym-aware matching (Excel = MS Excel = Advanced Excel = Spreadsheets)
  - Word-boundary matching (no false positives: "R" won't match "React")
  - Case-insensitive
  - Duplicate skill detection
  - Returns: found, missing, advanced_missing, found_core, found_advanced, found_soft
"""

import json
import os
import re
from typing import Dict, List, Set, Tuple

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# ── Cache loaded dataset ──────────────────────────────────────────────────────
_DATASET_CACHE: dict | None = None


def _load_dataset() -> dict:
    global _DATASET_CACHE
    if _DATASET_CACHE is None:
        path = os.path.join(DATA_DIR, 'skills_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _DATASET_CACHE = json.load(f)
    return _DATASET_CACHE


# ── Text normalisation ────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase + collapse whitespace + strip punctuation lightly."""
    text = text.lower()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


# ── Word-boundary aware search ────────────────────────────────────────────────
# Special handling for terms that are short or contain special chars.

_SPECIAL_CHAR_RE = re.compile(r'[+#@&|./]')

def _make_pattern(term: str) -> re.Pattern:
    """
    Build a regex that matches `term` as a whole phrase.
    Handles:
      - Terms with special chars (c++, c#, .net, etc.)
      - Short single letters (R, Go) using stricter boundaries
      - Normal multi-char terms with \b
    """
    is_single_word = len(term.split()) == 1

    if _SPECIAL_CHAR_RE.search(term):
        # Escape and use word-ish boundaries
        escaped = re.escape(term)
        return re.compile(r'(?<![a-z0-9])' + escaped + r'(?![a-z0-9])', re.IGNORECASE)

    if is_single_word and len(term) <= 2:
        # Very short terms (Go, R, C) — require surrounding spaces or line edges
        escaped = re.escape(term)
        return re.compile(r'(?:^|[\s,;(|/\-])' + escaped + r'(?:$|[\s,;)(|/\-])', re.IGNORECASE)

    # Normal multi-char / multi-word terms
    escaped = re.escape(term)
    return re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)


def _skill_present(resume_text_lower: str, synonyms: List[str]) -> bool:
    """Return True if ANY synonym of a skill is found in resume text."""
    for syn in synonyms:
        try:
            pattern = _make_pattern(syn)
            if pattern.search(resume_text_lower):
                return True
        except re.error:
            # Fallback: simple substring check
            if syn.lower() in resume_text_lower:
                return True
    return False


def _count_occurrences(resume_text_lower: str, synonyms: List[str]) -> int:
    """Count total occurrences of all synonyms in resume (for duplicate detection)."""
    total = 0
    for syn in synonyms:
        try:
            pattern = _make_pattern(syn)
            total += len(pattern.findall(resume_text_lower))
        except re.error:
            total += resume_text_lower.count(syn.lower())
    return total


# ── Field resolver ────────────────────────────────────────────────────────────

# Map any incoming field_key variation → canonical dataset key
# IMPORTANT: field_detector.py returns keys like "frontend_developer", "data_scientist", etc.
# These MUST be mapped here to the correct skills_dataset.json keys.
FIELD_ALIAS_MAP: Dict[str, str] = {
    # ── Keys from field_detector.py (underscore format) ──────────────────
    "frontend_developer":      "frontend_development",
    "backend_developer":       "software_engineering",
    "fullstack_developer":     "software_engineering",
    "java_developer":          "software_engineering",
    "python_developer":        "software_engineering",
    "software_engineer":       "software_engineering",
    "data_analyst":            "data_analyst",
    "data_scientist":          "data_science",
    "ml_ai_engineer":          "data_science",
    "devops_engineer":         "software_engineering",
    "cloud_engineer":          "software_engineering",
    "cybersecurity":           "software_engineering",
    "qa_engineer":             "software_engineering",
    "mobile_developer":        "software_engineering",
    "product_manager":         "software_engineering",
    "business_analyst":        "data_analyst",
    "blockchain":              "software_engineering",
    "embedded_iot":            "software_engineering",
    "digital_marketing":       "digital_marketing",
    "seo_specialist":          "digital_marketing",
    "content_writer":          "digital_marketing",
    "social_media_manager":    "digital_marketing",
    "brand_marketing":         "digital_marketing",
    "finance_analyst":         "financial_analysis",
    "accountant":              "accounting",
    "investment_banking":      "financial_analysis",
    "risk_compliance":         "financial_analysis",
    "equity_research":         "financial_analysis",
    "clinical_medicine":       "software_engineering",
    "clinical_research":       "software_engineering",
    "nursing":                 "software_engineering",
    "health_informatics":      "software_engineering",
    "pharmacy":                "software_engineering",
    "ui_ux_designer":          "ui_ux_design",
    "product_designer":        "ui_ux_design",
    "graphic_designer":        "ui_ux_design",
    "motion_designer":         "ui_ux_design",
    "corporate_law":           "software_engineering",
    "litigation":              "software_engineering",
    "ip_law":                  "software_engineering",
    "data_privacy_law":        "software_engineering",
    "hr_recruiter":            "hr",
    "talent_acquisition":      "hr",
    "hr_business_partner":     "hr",
    "compensation_benefits":   "hr",
    "learning_development":    "hr",
    "sales_executive":         "sales",
    "business_development":    "business_development",
    "operations_executive":    "operations",
    "customer_support":        "customer_support",
    "consulting":              "consulting",
    "management_trainee":      "software_engineering",
    "general_fresher":         "software_engineering",
    # ── Human-readable aliases (space format) ────────────────────────────
    "software_engineering":    "software_engineering",
    "software engineer":       "software_engineering",
    "software developer":      "software_engineering",
    "backend developer":       "software_engineering",
    "fullstack developer":     "software_engineering",
    "full stack developer":    "software_engineering",
    "java developer":          "software_engineering",
    "python developer":        "software_engineering",
    "mobile developer":        "software_engineering",
    "qa engineer":             "software_engineering",
    "frontend_development":    "frontend_development",
    "frontend developer":      "frontend_development",
    "front end developer":     "frontend_development",
    "ui developer":            "frontend_development",
    "web developer":           "frontend_development",
    "data_analyst":            "data_analyst",
    "data analyst":            "data_analyst",
    "business analyst":        "data_analyst",
    "bi analyst":              "data_analyst",
    "reporting analyst":       "data_analyst",
    "mis analyst":             "data_analyst",
    "data_science":            "data_science",
    "data scientist":          "data_science",
    "ml engineer":             "data_science",
    "machine learning engineer":"data_science",
    "ai engineer":             "data_science",
    "accounting":              "accounting",
    "accounts executive":      "accounting",
    "bookkeeper":              "accounting",
    "audit associate":         "accounting",
    "ca":                      "accounting",
    "chartered accountant":    "accounting",
    "financial_analysis":      "financial_analysis",
    "financial analyst":       "financial_analysis",
    "finance analyst":         "financial_analysis",
    "investment banking":      "financial_analysis",
    "equity research":         "financial_analysis",
    "risk analyst":            "financial_analysis",
    "hr":                      "hr",
    "hr recruiter":            "hr",
    "talent acquisition":      "hr",
    "hrbp":                    "hr",
    "human resources":         "hr",
    "sales":                   "sales",
    "sales executive":         "sales",
    "sales representative":    "sales",
    "account executive":       "sales",
    "inside sales":            "sales",
    "field sales":             "sales",
    "business development":    "business_development",
    "bde":                     "business_development",
    "bd manager":              "business_development",
    "customer support":        "customer_support",
    "customer service":        "customer_support",
    "helpdesk":                "customer_support",
    "technical support":       "customer_support",
    "operations":              "operations",
    "operations executive":    "operations",
    "supply chain":            "operations",
    "logistics":               "operations",
    "digital marketing":       "digital_marketing",
    "seo specialist":          "digital_marketing",
    "content writer":          "digital_marketing",
    "social media manager":    "digital_marketing",
    "brand marketing":         "digital_marketing",
    "growth_marketing":        "digital_marketing",
    "ui_ux_design":            "ui_ux_design",
    "ui/ux designer":          "ui_ux_design",
    "ui ux designer":          "ui_ux_design",
    "product designer":        "ui_ux_design",
    "graphic designer":        "ui_ux_design",
    "management consultant":   "consulting",
    "strategy consultant":     "consulting",
    "education":               "education",
    "teacher":                 "education",
    "professor":               "education",
    "lecturer":                "education",
    "product manager":         "software_engineering",
}


def resolve_field(raw_field: str) -> str:
    """
    Convert any field string to a canonical dataset key.
    Never falls back to software_engineering for non-tech roles.
    """
    if not raw_field:
        return "software_engineering"
    key = raw_field.strip().lower()
    # Direct lookup
    if key in FIELD_ALIAS_MAP:
        return FIELD_ALIAS_MAP[key]
    # Try dataset keys directly
    ds = _load_dataset()
    if key in ds:
        return key
    # Try removing underscores/spaces
    clean = key.replace('_', ' ').replace('-', ' ')
    if clean in FIELD_ALIAS_MAP:
        return FIELD_ALIAS_MAP[clean]
    # Partial match against alias map
    for alias, canonical in FIELD_ALIAS_MAP.items():
        if alias in key or key in alias:
            return canonical
    # Last resort: check if dataset has a matching key
    for ds_key in ds:
        if ds_key in key or key in ds_key:
            return ds_key
    return "software_engineering"


# ── Core analysis ─────────────────────────────────────────────────────────────

def _get_field_data(field_key: str) -> dict:
    """Load field data from dataset, with synonym resolution."""
    ds = _load_dataset()
    canonical = resolve_field(field_key)
    return ds.get(canonical, ds.get("software_engineering", {}))


def analyze_skills(text: str, field_key: str) -> dict:
    """
    Main skill analysis function.

    Returns:
        found          : list of canonical skill names found in resume
        missing        : list of core skill names NOT found
        advanced_missing: list of advanced skills NOT found
        found_core     : found core skills
        found_advanced : found advanced skills
        found_soft     : found soft skills
        duplicates     : skills mentioned redundantly (>1 synonym detected)
    """
    if not text or not text.strip():
        return {
            "found": [], "missing": [], "advanced_missing": [],
            "found_core": [], "found_advanced": [], "found_soft": [],
            "duplicates": [],
        }

    field_data    = _get_field_data(field_key)
    text_norm     = _normalise(text)

    core_skills_dict = field_data.get("core_skills", {}) or {}
    advanced_skills_dict = field_data.get("advanced_skills", {}) or {}
    soft_skills_dict = field_data.get("soft_skills", {}) or {}

    found_core:     List[str] = []
    missing_core:   List[str] = []
    found_adv:      List[str] = []
    missing_adv:    List[str] = []
    found_soft_lst: List[str] = []
    duplicates:     List[str] = []

    # ── Core skills ──────────────────────────────────────────────────
    for canonical_name, synonyms in core_skills_dict .items():
        if _skill_present(text_norm, synonyms):
            found_core.append(canonical_name)
            # Duplicate detection: >1 occurrence of any synonym variant
            if _count_occurrences(text_norm, synonyms) > 1:
                duplicates.append(canonical_name)
        else:
            missing_core.append(canonical_name)

    # ── Advanced skills ──────────────────────────────────────────────
    for canonical_name, synonyms in advanced_skills_dict .items():
        if _skill_present(text_norm, synonyms):
            found_adv.append(canonical_name)
        else:
            missing_adv.append(canonical_name)

    # ── Soft skills ──────────────────────────────────────────────────
    for canonical_name, synonyms in soft_skills_dict .items():
        if _skill_present(text_norm, synonyms):
            found_soft_lst.append(canonical_name)

    all_found = list(dict.fromkeys(found_core + found_adv + found_soft_lst))  # preserve order, dedup

    return {
        "found":            all_found,
        "missing":          missing_core,
        "advanced_missing": missing_adv,
        "found_core":       found_core,
        "found_advanced":   found_adv,
        "found_soft":       found_soft_lst,
        "duplicates":       list(dict.fromkeys(duplicates)),
    }


# ── Convenience: get soft skills only from free text ─────────────────────────

_GLOBAL_SOFT = [
    "communication","teamwork","leadership","problem solving","critical thinking",
    "time management","adaptability","creativity","collaboration","presentation",
    "negotiation","conflict resolution","decision making","emotional intelligence",
    "attention to detail","analytical thinking","self-motivated","integrity",
]

def get_soft_skills_from_text(text: str) -> List[str]:
    """Quick extraction of soft skills from any resume regardless of field."""
    tl = _normalise(text)
    return [s for s in _GLOBAL_SOFT if re.search(r'\b' + re.escape(s) + r'\b', tl)]
