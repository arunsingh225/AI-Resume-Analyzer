from fastapi import APIRouter
from app.services.field_detector import FIELD_MAP

router = APIRouter()

@router.get("/fields")
def get_fields():
    seen_domains = {}
    for key, meta in FIELD_MAP.items():
        d = meta["domain"]
        if d not in seen_domains:
            seen_domains[d] = []
        seen_domains[d].append({"key": key, "label": meta["display"]})
    return {"domains": seen_domains, "total_fields": len(FIELD_MAP)}

@router.get("/scoring-formula")
def scoring_formula():
    return {
        "formula": "Total = 0.35×Keyword + 0.20×Formatting + 0.20×Sections + 0.15×Experience + 0.10×Skills",
        "weights": {"keyword_relevance": "35%", "resume_formatting": "20%", "section_completeness": "20%", "experience_quality": "15%", "skill_coverage": "10%"},
        "notes": "Section weights vary by domain (e.g., portfolio matters more for design, publications for healthcare/legal)"
    }
