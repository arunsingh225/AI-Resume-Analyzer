"""
job_matcher.py — Field-aware Job Matching Engine

Features:
  - Universal field resolver (no wrong fallback to software_engineering)
  - Synonym-aware skill matching
  - Scoring: 65% skill overlap + 35% keyword overlap
  - Returns top 5 matched jobs per field+level
  - Correct company recommendations per exact field
"""

import json
import os
import re
from typing import List, Dict, Tuple, Optional

from app.services.skill_analyzer import resolve_field, _normalise, _skill_present

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

_JOBS_CACHE:      dict | None = None
_COMPANIES_CACHE: dict | None = None
_SKILLS_CACHE:    dict | None = None


def _load_jobs() -> dict:
    global _JOBS_CACHE
    if _JOBS_CACHE is None:
        path = os.path.join(DATA_DIR, 'jobs_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _JOBS_CACHE = json.load(f)
    return _JOBS_CACHE


def _load_companies() -> dict:
    global _COMPANIES_CACHE
    if _COMPANIES_CACHE is None:
        path = os.path.join(DATA_DIR, 'companies_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _COMPANIES_CACHE = json.load(f)
    return _COMPANIES_CACHE


def _load_skills_ds() -> dict:
    global _SKILLS_CACHE
    if _SKILLS_CACHE is None:
        path = os.path.join(DATA_DIR, 'skills_dataset.json')
        with open(path, 'r', encoding='utf-8') as f:
            _SKILLS_CACHE = json.load(f)
    return _SKILLS_CACHE


# ── Level normalisation ───────────────────────────────────────────────────────

def _resolve_level(level: str) -> str:
    level = (level or '').strip().lower()
    if level in ('fresher', 'entry', 'entry level', 'intern', 'trainee', '0', 'junior'):
        return 'fresher'
    if level in ('junior', 'associate', '1', '2'):
        return 'junior'
    if level in ('mid', 'mid-level', 'middle', '3', '4', '5'):
        return 'mid'
    if level in ('senior', 'lead', 'principal', 'staff', '6', '7', '8', '9'):
        return 'senior'
    return 'mid'


# ── Synonym-aware keyword matching ────────────────────────────────────────────

def _build_synonym_map(field_key: str) -> Dict[str, List[str]]:
    """
    Returns {canonical_name: [synonym1, synonym2, ...]} for the given field.
    Used to do synonym-aware skill matching when scoring jobs.
    """
    ds = _load_skills_ds()
    field_data = ds.get(field_key, {})
    synonym_map: Dict[str, List[str]] = {}
    for section in ('core_skills', 'advanced_skills', 'soft_skills'):
        for canonical, syns in field_data.get(section, {}).items():
            synonym_map[canonical.lower()] = [s.lower() for s in syns]
    return synonym_map


def _skill_match_score(
    resume_text_norm: str,
    found_skills: List[str],
    required_skills: List[str],
    synonym_map: Dict[str, List[str]],
) -> Tuple[float, List[str], List[str]]:
    """
    Match required_skills against resume using synonym expansion.
    Returns (ratio 0-1, matched_list, missing_list).
    """
    if not required_skills:
        return 0.0, [], []

    matched  = []
    missing  = []
    found_lower = {s.lower() for s in found_skills}

    for req in required_skills:
        req_l = req.lower()

        # 1. Direct match against found_skills
        if req_l in found_lower:
            matched.append(req)
            continue

        # 2. Synonym expansion: look up synonyms in the map
        synonyms = synonym_map.get(req_l, [req_l])
        if _skill_present(resume_text_norm, synonyms):
            matched.append(req)
            continue

        # 3. Partial substring check (catches "Advanced Excel" matching "Excel")
        found_in_text = any(
            req_l in s_l or s_l in req_l
            for s_l in found_lower
        )
        if found_in_text:
            matched.append(req)
            continue

        missing.append(req)

    ratio = len(matched) / max(len(required_skills), 1)
    return ratio, matched, missing


def _keyword_match_score(
    resume_text_norm: str,
    keywords: List[str],
) -> float:
    """Simple keyword overlap ratio against resume text (case-insensitive)."""
    if not keywords:
        return 0.0
    hits = sum(
        1 for kw in keywords
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', resume_text_norm)
        or kw.lower() in resume_text_norm
    )
    return hits / max(len(keywords), 1)


# ── Main matching function ────────────────────────────────────────────────────

def match_jobs(
    text: str,
    field_key: str,
    level: str,
    found_skills: List[str],
) -> List[dict]:
    """
    Match the resume against jobs in the dataset.

    Algorithm:
      score = 0.65 × skill_match + 0.35 × keyword_match
      capped at 97%

    Returns up to 6 sorted results.
    """
    jobs_data = _load_jobs()
    canonical = resolve_field(field_key)
    level_key = _resolve_level(level)

    text_norm    = _normalise(text)
    synonym_map  = _build_synonym_map(canonical)

    # Get jobs for this field
    field_jobs: dict = jobs_data.get(canonical, {})

    # If field has no jobs, try a graceful broadening for closely related fields
    if not field_jobs:
        # Map non-tech fields with thin job datasets to closest parent
        PARENT_MAP = {
            "consulting":       "sales",          # consulting has strategy
            "education":        "operations",     # operations overlap
        }
        parent = PARENT_MAP.get(canonical)
        if parent:
            field_jobs = jobs_data.get(parent, {})
        if not field_jobs:
            return []

    # Level fallback order
    LEVEL_FALLBACK = {
        'fresher': ['fresher', 'junior', 'mid'],
        'junior':  ['junior', 'fresher', 'mid'],
        'mid':     ['mid', 'junior', 'senior'],
        'senior':  ['senior', 'mid'],
    }

    job_list: List[dict] = []
    for lvl in LEVEL_FALLBACK.get(level_key, ['mid']):
        if lvl in field_jobs:
            job_list = field_jobs[lvl]
            break

    if not job_list:
        # Last attempt: any level from this field
        for lvl in ('mid', 'fresher', 'junior', 'senior'):
            if lvl in field_jobs:
                job_list = field_jobs[lvl]
                break

    if not job_list:
        return []

    results = []
    for job in job_list:
        required  = job.get('required_skills', [])
        kw_list   = job.get('job_match_keywords', required)

        skill_ratio, matched, missing = _skill_match_score(
            text_norm, found_skills, required, synonym_map
        )
        kw_ratio = _keyword_match_score(text_norm, kw_list)

        score = round(min(0.65 * skill_ratio + 0.35 * kw_ratio, 0.97) * 100, 1)

        results.append({
            'role':           job.get('role', 'Unknown Role'),
            'match_percent':  score,
            'required_skills':required,
            'matched_skills': matched,
            'missing_skills': missing[:5],
            'companies':      job.get('companies', []),
            'avg_salary':     job.get('avg_salary', 'N/A'),
            'level':          level_key,
        })

    results.sort(key=lambda x: x['match_percent'], reverse=True)
    return results[:6]


# ── Company recommendations ───────────────────────────────────────────────────

def get_company_recommendations(field_key: str, level: str) -> dict:
    companies_data = _load_companies()

    # 🔥 mapping fix (MOST IMPORTANT)
    company_key_map = {
        "accounting": "accountant",
        "financial_analysis": "finance_analyst",
        "sales": "sales_executive",
        "hr": "hr_recruiter",
        "frontend_development": "frontend_developer",
        "software_engineering": "software_engineer",
        "data_science": "data_scientist",
        "ui_ux_design": "ui_ux_designer",
        "product_management": "product_manager",
        "operations": "operations_executive",
        "mobile_development": "mobile_developer",
        "devops_cloud": "devops_engineer",
        "cybersecurity": "cybersecurity_analyst",
        "consulting": "management_consultant",
        "education": "education_professional",
        "marketing": "marketing_specialist"
    }

    # 🔥 apply mapping
    canonical = company_key_map.get(field_key, field_key)

    field_companies = companies_data.get(canonical, {})

    return {
        "mncs": [
            {"name": c["name"], "ats_strictness": c.get("ats_strictness", "medium"),
             "preferred_skills": c.get("preferred_skills", [])}
            for c in field_companies.get("mncs", [])[:8]
        ],
        "startups": [
            {"name": c["name"], "ats_strictness": c.get("ats_strictness", "medium"),
             "preferred_skills": c.get("preferred_skills", [])}
            for c in field_companies.get("startups", [])[:8]
        ],
        "product_companies": [
            {"name": c["name"], "ats_strictness": c.get("ats_strictness", "medium"),
             "preferred_skills": c.get("preferred_skills", [])}
            for c in field_companies.get("product_companies", [])[:6]
        ],
    }
