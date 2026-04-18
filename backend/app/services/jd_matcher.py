"""
JD Matcher — compares resume text against a job description.
Uses TF-IDF cosine similarity + keyword overlap for a realistic match score.
"""
import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOP_WORDS = {
    "and","the","for","with","are","was","were","has","have","had","been","will",
    "would","could","should","may","might","this","that","from","into","over",
    "under","through","about","after","before","during","also","both","each",
    "more","most","other","some","such","than","then","they","their","them",
    "these","those","when","where","which","while","who","all","any","can","not",
    "our","out","its","own","per","etc","use","used","using","work","works",
    "year","years","team","teams","based","able","new","good","high","well",
    "strong","large","small","make","must","need","needs","will","shall",
    "include","including","within","across","ensure","manage","support",
    "experience","ability","skills","knowledge","understanding","working",
    "responsible","role","candidate","position","job","company","opportunity",
}


def clean(text: str) -> str:
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return [w for w in clean(text).split() if w not in STOP_WORDS and len(w) > 2]


def extract_phrases(text: str, n: int = 2) -> List[str]:
    """Extract 1-gram and 2-gram meaningful phrases."""
    tokens = tokenize(text)
    unigrams = tokens
    bigrams  = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]
    return list(set(unigrams + bigrams))


def tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between resume and JD using TF-IDF."""
    try:
        vec = TfidfVectorizer(
            stop_words=list(STOP_WORDS),
            ngram_range=(1, 2),
            max_features=5000,
        )
        matrix = vec.fit_transform([clean(resume_text), clean(jd_text)])
        sim    = cosine_similarity(matrix[0], matrix[1])[0][0]
        return round(float(sim), 4)
    except Exception:
        return 0.0


def keyword_overlap(resume_text: str, jd_text: str) -> Tuple[List[str], List[str]]:
    """Find keywords from JD that are / aren't in the resume."""
    jd_kw     = set(extract_phrases(jd_text))
    resume_kw = set(extract_phrases(resume_text))
    found   = sorted(jd_kw & resume_kw)
    missing = sorted(jd_kw - resume_kw)
    return found, missing


def skill_match(resume_text: str, jd_text: str) -> Tuple[List[str], List[str]]:
    """Extract likely skill tokens (capitalized or short technical terms) from JD."""
    skill_pattern = re.compile(
        r'\b(python|java|javascript|typescript|react|node|sql|aws|azure|gcp|docker|'
        r'kubernetes|terraform|git|html|css|machine learning|deep learning|nlp|'
        r'tensorflow|pytorch|pandas|excel|power bi|tableau|figma|sketch|'
        r'photoshop|illustrator|seo|google analytics|hubspot|salesforce|'
        r'jira|agile|scrum|ci/cd|linux|bash|spring|django|flask|fastapi|'
        r'mongodb|postgresql|redis|kafka|spark|hadoop|airflow|'
        r'communication|leadership|teamwork|problem.solving|analytical|'
        r'financial modeling|dcf|valuation|bloomberg|cfa|gaap|ifrs|'
        r'clinical|patient care|ehr|hipaa|gcp clinical|'
        r'recruitment|talent acquisition|hris|okr|kpi)\b',
        re.IGNORECASE
    )
    jd_skills     = set(m.group(0).lower() for m in skill_pattern.finditer(jd_text))
    resume_skills = set(m.group(0).lower() for m in skill_pattern.finditer(resume_text))
    matched  = sorted(jd_skills & resume_skills)
    missing  = sorted(jd_skills - resume_skills)
    return matched, missing


def generate_suggestions(missing_skills: List[str], missing_keywords: List[str], match_pct: float) -> List[str]:
    suggestions = []
    if match_pct < 50:
        suggestions.append("Your resume has low overlap with this JD. Rewrite your Summary section to include the job title and top 5 keywords from the JD.")
    if match_pct < 70:
        suggestions.append("Add a 'Key Skills' section that mirrors the exact skill names used in the JD.")

    if missing_skills:
        top = missing_skills[:5]
        suggestions.append(f"Missing technical skills from JD: {', '.join(top)}. Add these if you have experience, or pursue certifications.")

    if missing_keywords:
        top_kw = [k for k in missing_keywords if len(k.split()) <= 2][:6]
        if top_kw:
            suggestions.append(f"Use these exact JD phrases in your resume: {', '.join(top_kw)}")

    suggestions += [
        "Mirror the job title in your professional summary.",
        "Quantify achievements that match JD requirements (%, revenue, team size).",
        "Ensure your experience bullet points use the same verb tense and phrasing as the JD.",
    ]
    return suggestions[:6]


def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """Master function — returns full JD match analysis with optional semantic AI."""
    if not resume_text.strip() or not jd_text.strip():
        raise ValueError("Both resume text and job description are required.")

    tfidf_sim         = tfidf_similarity(resume_text, jd_text)
    kw_found, kw_miss = keyword_overlap(resume_text, jd_text)
    sk_found, sk_miss = skill_match(resume_text, jd_text)

    kw_score = len(kw_found) / max(len(kw_found) + len(kw_miss), 1)
    sk_score = len(sk_found) / max(len(sk_found) + len(sk_miss), 1)

    # ── Semantic AI enhancement (sentence-transformers) ──
    match_method = "tfidf_only"
    blended_sim = tfidf_sim
    semantic_score_pct = None
    try:
        from app.services.semantic_matcher import enhanced_jd_match, is_available
        if is_available():
            blended_sim, match_method = enhanced_jd_match(resume_text, jd_text, tfidf_sim)
            sem_raw = (blended_sim - 0.40 * tfidf_sim) / 0.60 if match_method != "tfidf_only" else None
            semantic_score_pct = round(sem_raw * 100, 1) if sem_raw is not None else None
    except Exception:
        pass

    # Weighted match: 40% similarity + 35% keyword overlap + 25% skill match
    raw = 0.40 * blended_sim + 0.35 * kw_score + 0.25 * sk_score
    match_pct = round(min(raw * 100, 98), 1)

    suggestions = generate_suggestions(sk_miss, kw_miss[:20], match_pct)

    return {
        "match_percent":      match_pct,
        "tfidf_score":        round(tfidf_sim * 100, 1),
        "semantic_score":     semantic_score_pct,
        "keyword_overlap_pct":round(kw_score * 100, 1),
        "skill_overlap_pct":  round(sk_score * 100, 1),
        "match_method":       match_method,
        "keywords_found":     kw_found[:30],
        "keywords_missing":   kw_miss[:30],
        "skills_matched":     sk_found,
        "skills_missing":     sk_miss,
        "suggestions":        suggestions,
        "verdict": (
            "Excellent match — apply immediately." if match_pct >= 78 else
            "Good match — minor tailoring needed." if match_pct >= 60 else
            "Moderate match — significant tailoring required." if match_pct >= 45 else
            "Low match — strongly consider rewriting your resume for this role."
        )
    }

