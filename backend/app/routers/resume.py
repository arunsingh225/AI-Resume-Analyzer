from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.parser import extract_from_pdf, extract_from_docx
from app.services.field_detector import detect_field, get_display_name, get_domain, FIELD_MAP
from app.services.ats_scorer import compute_ats_score
from app.services.skill_analyzer import analyze_skills
from app.services.job_matcher import match_jobs, get_company_recommendations
from app.services.course_recommender import recommend_courses
from app.services.roadmap_generator import generate_roadmap

import json
import hashlib
from typing import Optional
from app.utils.auth_utils import get_optional_user
from app.database import User, Analysis, get_db
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter()
MAX_SIZE = 10 * 1024 * 1024  # 10MB

FRESHER_TIPS = {
    "technical": ["Build 2–3 GitHub projects with full README documentation","Get AWS Cloud Practitioner or Google IT Support cert (both accessible)","Contribute to open source — even documentation PRs count","Solve 100 LeetCode problems before applying to product companies","Include GPA if ≥ 7.5/3.5","Add your tech stack prominently and link to live demos"],
    "frontend_development": ["Build a portfolio site with 3+ real project demos","Learn TypeScript and use it in at least one project","Contribute a component to a popular open-source UI library","Get Figma basics — collaboration with designers is essential","Show performance scores (Lighthouse) for your projects"],
    "data_science": ["Compete on Kaggle and link your profile","Publish a Jupyter notebook analysis on GitHub","Complete Andrew Ng's Machine Learning Specialization first","Learn SQL deeply — it's tested in every DS interview","Build an end-to-end ML project deployed on Hugging Face Spaces"],
    "investment_banking": ["CFA Level 1 enrollment signals serious commitment","Build DCF models for public companies and add to portfolio","Get Bloomberg Market Concepts (BMC) certificate — free via campus","Apply to summer internships 6 months before intake","Network with IB analysts on LinkedIn — most positions are referral-based"],
    "ui_ux_design": ["Build a Behance portfolio with 3 complete case studies","Show your UX process: research → define → ideate → prototype → test","Get the Google UX Design Professional Certificate (Coursera)","Do 5 unprompted app redesigns — great for portfolio depth","Join ADPList and find a mentor"],
    "corporate_law": ["Publish a legal article on SCC Online Blog or Bar & Bench","Participate in moot court competitions — list achievements","Get SCC Online access through your law school","Apply for internships at AZB, CAM, SAM in your 2nd year","Learn MS Word legal formatting and track changes"],
    "talent_acquisition": ["Get LinkedIn Recruiter Lite access through a 30-day trial","Complete SHRM Essentials of HR online course","Practice Boolean search strings for 10 different roles","Build a mock JD library for 20 different positions","Shadow a TA manager during a hiring cycle"],
    "digital_marketing": ["Get Google Analytics 4 and Google Ads certified (both free)","Run a real ₹500 Facebook Ads campaign and document ROAS","Build an SEO content plan and publish 5 optimized blog posts","Complete HubSpot Marketing Software Certification (free)","Create a case study doc showing before/after campaign results"],
}

STRENGTHS_LOGIC = {
    "high_ats": "Strong overall ATS compatibility — top {pct}% for this field",
    "good_keywords": "Excellent keyword alignment for {field} domain",
    "good_format": "Well-structured resume with strong formatting signals",
    "many_skills": "Broad and relevant skill set: {count} skills detected",
    "advanced_skills": "Advanced skills detected: {skills}",
    "soft_skills": "Soft skills mentioned — important for culture-fit screening",
}

def build_sw(ats: dict, skills: dict, level: str, field_key: str, domain: str) -> dict:
    strengths, weaknesses, recs = [], [], []
    total = ats.get("total", 0)
    if total >= 70: strengths.append(f"Strong ATS score of {total:.0f} — competitive for {field_key.replace('_',' ').title()} roles")
    if ats.get("keyword_score", 0) >= 65: strengths.append(f"Good keyword density for {field_key.replace('_',' ').title()} domain")
    if ats.get("formatting_score", 0) >= 65: strengths.append("Resume formatting follows ATS-friendly conventions")
    if len(skills.get("found", [])) >= 10: strengths.append(f"{len(skills['found'])} relevant skills detected — strong profile")
    if skills.get("found_advanced"): strengths.append(f"Advanced skills present: {', '.join(skills['found_advanced'][:3])}")
    if skills.get("found_soft"): strengths.append("Soft skills explicitly mentioned — valuable for culture screening")

    if total < 50: weaknesses.append(f"ATS score {total:.0f} is below average — below 50% may auto-reject in ATS systems")
    if ats.get("keyword_score", 0) < 50: weaknesses.append("Low keyword density — add more field-specific keywords to pass ATS filters")
    if ats.get("formatting_score", 0) < 50: weaknesses.append("Formatting issues detected — use bullet points, action verbs, and quantified results")
    if len(skills.get("missing", [])) > 5: weaknesses.append(f"{len(skills['missing'])} core skills missing for this field — prioritize adding them")
    if skills.get("duplicates"): weaknesses.append(f"Duplicate skills found ({', '.join(skills['duplicates'][:3])}) — consolidate these")
    if not skills.get("found_soft"): weaknesses.append("No soft skills mentioned — add communication, teamwork, or leadership explicitly")
    if not any(s.get("present") for s in ats.get("section_details_raw", []) if s.get("name","").lower() == "certifications"):
        weaknesses.append("No certifications section — adding one certification significantly improves ATS score")

    if level in ("fresher", "junior"):
        recs += ["Build 2–3 portfolio projects with GitHub links and live demos", "Get at least one recognized certification for this field", "Add a tailored professional summary for each application", "Quantify any internship or project outcomes with real numbers"]
    else:
        recs += ["Quantify every achievement: 'Reduced latency by 35%', 'Grew revenue by ₹2Cr'", "Tailor your resume keyword set per job description", "Add leadership or mentoring examples even in IC roles", "Update certifications — anything older than 3 years loses ATS weight"]

    if not strengths: strengths.append("Resume submitted — begin analysis and improvements")
    if not weaknesses: weaknesses.append("No major weaknesses found — focus on quantifying achievements further")
    return {"strengths": strengths, "weaknesses": weaknesses, "recommendations": recs}

def get_fresher_tips(level: str, field_key: str, domain: str) -> list:
    if level not in ("fresher", "junior"):
        return []
    tips = FRESHER_TIPS.get(field_key, FRESHER_TIPS.get(domain, FRESHER_TIPS.get("technical", [])))
    return tips

@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    name = file.filename or ""
    is_pdf  = name.lower().endswith(".pdf")
    is_docx = name.lower().endswith(".docx") or name.lower().endswith(".doc")
    if not (is_pdf or is_docx):
        raise HTTPException(400, "Only PDF and DOCX files are accepted.")

    raw = await file.read()
    if len(raw) > MAX_SIZE:
        raise HTTPException(400, "File exceeds 10MB limit.")
    if len(raw) < 10:
        raise HTTPException(400, "File is empty or corrupted.")

    # Magic byte validation — verify actual file content, not just extension
    PDF_MAGIC  = b'%PDF'
    DOCX_MAGIC = b'PK\x03\x04'  # ZIP/DOCX signature
    if is_pdf and not raw[:4].startswith(PDF_MAGIC):
        raise HTTPException(400, "File content doesn't match PDF format. Ensure you're uploading a valid PDF.")
    if is_docx and not raw[:4].startswith(DOCX_MAGIC):
        raise HTTPException(400, "File content doesn't match DOCX format. Ensure you're uploading a valid Word document.")

    try:
        text, meta = extract_from_pdf(raw) if is_pdf else extract_from_docx(raw)
    except ValueError as e:
        raise HTTPException(422, str(e))

    field_key, domain, confidence, _ = detect_field(text)
    level  = meta["experience_level"]
    years  = meta["years_experience"]

    skills = analyze_skills(text, field_key)
    found  = skills["found"]

    ats_raw = compute_ats_score(text, field_key, domain, years, found)
    sec_details = ats_raw.pop("section_details", [])
    kw_found    = ats_raw.pop("keywords_found", [])
    kw_missing  = ats_raw.pop("keywords_missing", [])

    jobs      = match_jobs(text, field_key, level, found)
    companies = get_company_recommendations(field_key, level)
    missing   = skills["missing"] + skills["advanced_missing"]
    courses   = recommend_courses(missing, domain, level)
    roadmap   = generate_roadmap(field_key, domain, level, missing)

    # pass raw section data to sw builder
    ats_raw["section_details_raw"] = sec_details
    sw        = build_sw(ats_raw, skills, level, field_key, domain)
    ats_raw.pop("section_details_raw", None)

    result = {
        "candidate_name":    meta["name"],
        "email":             meta.get("email",""),
        "phone":             meta.get("phone",""),
        "detected_field":    get_display_name(field_key),
        "detected_field_key":field_key,
        "detected_subfield": get_display_name(field_key),
        "experience_level":  level,
        "years_experience":  round(years, 1),
        "field_confidence":  round(confidence * 100, 1),
        "file_type":         meta["file_type"],
        "ats_score":         ats_raw,
        "section_scores":    sec_details,
        "skill_analysis":    {"found": found, "missing": skills["missing"], "advanced_missing": skills["advanced_missing"], "duplicates": skills["duplicates"], "found_core": skills["found_core"], "found_advanced": skills["found_advanced"], "found_soft": skills["found_soft"]},
        "job_matches":       jobs,
        "company_recommendations": companies,
        "course_recommendations":  courses,
        "roadmap":           roadmap,
        "strengths_weaknesses": sw,
        "keywords_found":    kw_found,
        "keywords_missing":  kw_missing,
        "fresher_tips":      get_fresher_tips(level, field_key, domain),
        "raw_text_preview":  text[:600] + "..." if len(text) > 600 else text,
    }

    # ── Save to analysis history ──
    if current_user:
        try:
            file_hash = hashlib.sha256(raw).hexdigest()
            analysis_record = Analysis(
                user_id=current_user.id,
                filename=name,
                file_type=meta["file_type"],
                detected_field=get_display_name(field_key),
                detected_subfield=get_display_name(field_key),
                ats_score=ats_raw.get("total", 0),
                grade=ats_raw.get("grade", ""),
                experience_level=level,
                candidate_name=meta["name"],
                result_json=json.dumps(result, default=str),
                file_hash=file_hash,
            )
            db.add(analysis_record)
            db.commit()
            result["analysis_id"] = analysis_record.id
        except Exception:
            db.rollback()  # Don't fail the analysis if history save fails

    return JSONResponse(result)

