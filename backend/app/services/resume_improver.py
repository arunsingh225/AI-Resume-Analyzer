"""
Resume Improver — rule-based improvement engine.
No external API needed. Improves bullet points, adds action verbs,
enhances wording, detects weak phrases.
"""
import re
from typing import List, Dict, Tuple

# ── Weak phrase replacements ────────────────────────────────────────
WEAK_REPLACEMENTS = {
    r'\bresponsible for\b':     'Led',
    r'\bhelped (with|to)\b':    'Contributed to',
    r'\bworked on\b':           'Developed',
    r'\bwas involved in\b':     'Participated in',
    r'\bdid\b':                 'Executed',
    r'\bdealt with\b':          'Managed',
    r'\bhandled\b':             'Oversaw',
    r'\btried to\b':            'Achieved',
    r'\bassisted in\b':         'Supported',
    r'\bpart of\b':             'Contributed to',
    r'\bgood at\b':             'Proficient in',
    r'\bknowledgeable about\b': 'Experienced in',
    r'\bfamiliar with\b':       'Proficient in',
    r'\bhave experience in\b':  'Experienced in',
    r'\bexposure to\b':         'Experienced in',
    r'\bbasic knowledge of\b':  'Foundational expertise in',
}

# ── Strong action verbs by category ────────────────────────────────
ACTION_VERBS_BY_SECTION = {
    "experience": [
        "Architected","Built","Delivered","Deployed","Designed","Developed",
        "Drove","Engineered","Enhanced","Established","Executed","Facilitated",
        "Generated","Implemented","Improved","Launched","Led","Managed",
        "Optimized","Overhauled","Pioneered","Reduced","Revamped","Scaled",
        "Shipped","Spearheaded","Streamlined","Transformed","Upgraded",
    ],
    "achievement": [
        "Achieved","Attained","Awarded","Boosted","Earned","Exceeded",
        "Grew","Increased","Maximized","Outperformed","Surpassed","Won",
    ],
    "leadership": [
        "Coached","Coordinated","Cultivated","Directed","Guided","Headed",
        "Inspired","Mentored","Motivated","Oversaw","Recruited","Supervised",
    ],
    "analysis": [
        "Analyzed","Assessed","Audited","Evaluated","Forecasted","Identified",
        "Investigated","Measured","Modeled","Researched","Studied","Tracked",
    ],
}

ALL_ACTION_VERBS = sum(ACTION_VERBS_BY_SECTION.values(), [])

# ── Weak starters (lines that don't begin with an action verb) ──────
WEAK_STARTERS = re.compile(
    r'^(i |we |our |the |a |an |was |were |is |am |are |have |had |has )',
    re.IGNORECASE
)

# ── Quantification hints ────────────────────────────────────────────
QUANT_PATTERNS = re.compile(
    r'\b(\d+%|\d+\s*(million|billion|lakh|crore|k\b|users|clients|projects|'
    r'team|members|employees|countries|regions|products|orders|requests|'
    r'transactions|tickets|ms\b|seconds\b|hrs\b|hours\b))\b',
    re.IGNORECASE
)


def detect_weak_phrases(text: str) -> List[Dict]:
    issues = []
    for pattern, replacement in WEAK_REPLACEMENTS.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            issues.append({
                "original":    m.group(0),
                "replacement": replacement,
                "context":     text[max(0, m.start()-30):m.end()+50].strip(),
            })
    return issues


def improve_bullet(line: str) -> Tuple[str, str]:
    """
    Improve a single bullet point.
    Returns (improved_line, reason).
    """
    original = line.strip()
    improved = original
    reason   = []

    # 1. Replace weak phrases
    for pattern, repl in WEAK_REPLACEMENTS.items():
        new = re.sub(pattern, repl, improved, flags=re.IGNORECASE)
        if new != improved:
            reason.append(f"Replaced weak phrase with stronger verb")
            improved = new

    # 2. Fix weak starters — prepend a strong verb
    if WEAK_STARTERS.match(improved):
        improved = f"Led — {improved}"
        reason.append("Added action verb at start")

    # 3. Capitalise first letter
    if improved and improved[0].islower():
        improved = improved[0].upper() + improved[1:]
        reason.append("Capitalized first word")

    # 4. Suggest quantification if no numbers present
    quant_hint = ""
    if not QUANT_PATTERNS.search(improved) and len(improved.split()) > 5:
        quant_hint = "Add a metric: e.g. 'by 30%', 'for 10,000 users', 'saving ₹5L annually'"

    return improved, " | ".join(reason) if reason else "No change needed", quant_hint


def improve_summary(summary: str) -> Dict:
    """Return an improved summary and suggestions."""
    suggestions = []
    improved    = summary.strip()

    if len(improved.split()) < 30:
        suggestions.append("Your summary is too short. Aim for 3–4 sentences covering: who you are, your top skills, years of experience, and what value you bring.")
    if not any(v.lower() in improved.lower() for v in ["years", "yr", "experience"]):
        suggestions.append("Mention your years of experience explicitly in the summary.")
    if not any(c.isdigit() for c in improved):
        suggestions.append("Add at least one quantified achievement or metric in your summary.")
    if re.search(r'\bresponsible for\b|\bfamiliar with\b|\bexposure to\b', improved, re.IGNORECASE):
        for pattern, repl in WEAK_REPLACEMENTS.items():
            improved = re.sub(pattern, repl, improved, flags=re.IGNORECASE)
        suggestions.append("Replaced weak phrases with stronger language.")

    return {"original": summary, "improved": improved, "suggestions": suggestions}


def extract_bullets(text: str) -> List[str]:
    """Extract bullet-point lines from resume text."""
    lines = text.split('\n')
    bullets = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('•', '-', '*', '–', '→', '·')):
            bullets.append(stripped.lstrip('•-*–→· ').strip())
        elif len(stripped.split()) >= 5 and stripped[0].isupper():
            # Looks like a sentence-style bullet
            bullets.append(stripped)
    return [b for b in bullets if b]


def get_section_suggestions(text: str) -> Dict[str, List[str]]:
    """High-level suggestions per section."""
    tl = text.lower()
    suggestions = {}

    # Summary
    if any(w in tl for w in ["summary", "profile", "objective"]):
        s = []
        if "year" not in tl and "yr" not in tl:
            s.append("Add your years of experience to the summary.")
        if not re.search(r'\d', text[:500]):
            s.append("Include a quantified result in the summary (e.g. 'increased sales by 25%').")
        if s: suggestions["Summary"] = s

    # Experience
    exp_section = re.search(r'(experience|employment|career)(.*?)(?=education|skills|projects|certif|$)',
                             tl, re.DOTALL)
    if exp_section:
        s = []
        exp_text = exp_section.group(0)
        bullets  = extract_bullets(exp_text)
        weak_count = sum(1 for b in bullets if WEAK_STARTERS.match(b))
        if weak_count > 2:
            s.append(f"{weak_count} bullet points start without a strong action verb. Begin each with a past-tense action verb (e.g., Led, Built, Improved).")
        no_quant = sum(1 for b in bullets if not QUANT_PATTERNS.search(b))
        if no_quant > len(bullets) * 0.6:
            s.append("Most bullets lack quantification. Add numbers, percentages, or scale indicators to at least 50% of bullets.")
        if s: suggestions["Experience"] = s

    # Skills
    if "skills" in tl:
        s = []
        if "proficient" not in tl and "advanced" not in tl and "expert" not in tl:
            s.append("Group skills by proficiency level: Expert / Proficient / Familiar.")
        if s: suggestions["Skills"] = s

    # Missing sections
    missing = []
    if "certif" not in tl: missing.append("Certifications")
    if "project" not in tl: missing.append("Projects")
    if "summary" not in tl and "profile" not in tl: missing.append("Professional Summary")
    if missing:
        suggestions["Missing Sections"] = [f"Add: {', '.join(missing)} to improve ATS score."]

    return suggestions


def improve_resume(resume_text: str) -> dict:
    """Master improvement function."""
    bullets  = extract_bullets(resume_text)
    improved_bullets = []
    for b in bullets[:20]:   # process up to 20 bullets
        imp, reason, quant = improve_bullet(b)
        improved_bullets.append({
            "original":    b,
            "improved":    imp,
            "reason":      reason,
            "quant_hint":  quant,
            "changed":     imp.strip() != b.strip(),
        })

    # Summary improvement
    summary_match = re.search(
        r'(summary|profile|objective)[:\s\n]+(.*?)(?=\n[A-Z][a-z]|\nexperience|\neducation|$)',
        resume_text, re.IGNORECASE | re.DOTALL
    )
    summary_result = None
    if summary_match:
        summary_result = improve_summary(summary_match.group(2).strip()[:500])

    section_suggestions = get_section_suggestions(resume_text)

    # Overall tips
    overall_tips = [
        "Use consistent date formatting throughout (e.g., Jan 2022 – Mar 2024).",
        "Keep resume to 1–2 pages for under 8 years of experience.",
        "Remove personal information like age, photo, marital status for ATS.",
        "Use the same keywords from the job description you're applying to.",
        "Save your resume as a PDF but ensure it is text-selectable (not scanned).",
        "Put your most recent and relevant experience first.",
    ]

    changed_count = sum(1 for b in improved_bullets if b["changed"])

    return {
        "improved_bullets":   improved_bullets,
        "summary_improvement":summary_result,
        "section_suggestions":section_suggestions,
        "overall_tips":       overall_tips,
        "stats": {
            "bullets_analyzed":changed_count,
            "bullets_improved":changed_count,
            "total_bullets":  len(improved_bullets),
        }
    }
