from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ATSScore(BaseModel):
    total: float
    keyword_score: float
    formatting_score: float
    section_score: float
    experience_score: float
    skill_score: float
    grade: str
    interpretation: str


class SectionScore(BaseModel):
    name: str
    present: bool
    score: float
    feedback: str
    suggestions: List[str]


class SkillAnalysis(BaseModel):
    found: List[str]
    missing: List[str]
    advanced_missing: List[str]
    duplicates: List[str]
    found_core: List[str]
    found_advanced: List[str]
    found_soft: List[str]


class JobMatch(BaseModel):
    role: str
    match_percent: float
    required_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    companies: List[str]
    avg_salary: str
    level: str


class CourseRecommendation(BaseModel):
    skill: str
    course_name: str
    platform: str
    url: str
    duration: str
    level: str
    rating: float


class RoadmapWeek(BaseModel):
    week: int
    title: str
    tasks: List[str]
    skills: List[str]
    resources: List[str]


class CompanyEntry(BaseModel):
    name: str
    ats_strictness: Optional[str] = "medium"
    preferred_skills: Optional[List[str]] = []


class CompanyRecommendations(BaseModel):
    mncs: List[CompanyEntry]
    startups: List[CompanyEntry]
    product_companies: List[CompanyEntry]


class StrengthsWeaknesses(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class ResumeAnalysisResult(BaseModel):
    candidate_name: str
    email: str
    phone: str
    detected_field: str
    detected_field_key: str
    detected_subfield: str
    experience_level: str
    years_experience: float
    field_confidence: float
    ats_score: ATSScore
    section_scores: List[SectionScore]
    skill_analysis: SkillAnalysis
    job_matches: List[JobMatch]
    company_recommendations: CompanyRecommendations
    course_recommendations: List[CourseRecommendation]
    roadmap: List[RoadmapWeek]
    strengths_weaknesses: StrengthsWeaknesses
    keywords_found: List[str]
    keywords_missing: List[str]
    fresher_tips: List[str]
    raw_text_preview: str
    file_type: str
