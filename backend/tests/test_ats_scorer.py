"""
Unit tests for the ATS scorer module.
"""
import pytest
from app.services.ats_scorer import compute_ats_score


class TestComputeATSScore:
    def test_returns_required_fields(self):
        result = compute_ats_score(
            "Python developer with 3 years experience in Django and Flask",
            "python_developer", "technical", 3.0, ["python", "django", "flask"]
        )
        assert "total" in result
        assert "grade" in result
        assert "keyword_score" in result
        assert "formatting_score" in result
        assert "section_score" in result
        assert "experience_score" in result
        assert "skill_score" in result

    def test_score_in_bounds(self):
        result = compute_ats_score(
            "Basic resume text with some skills",
            "general_fresher", "general", 0, []
        )
        assert 0 <= result["total"] <= 100

    def test_score_increases_with_keywords(self):
        sparse = compute_ats_score(
            "generic resume text",
            "python_developer", "technical", 0, []
        )
        rich = compute_ats_score(
            "python django flask fastapi rest api sql git pandas pytest docker kubernetes aws deployed optimized built",
            "python_developer", "technical", 3.0,
            ["python", "django", "flask", "fastapi", "sql", "git", "pandas"]
        )
        assert rich["total"] > sparse["total"]

    def test_grade_assignment(self):
        result = compute_ats_score(
            "x" * 100,
            "general_fresher", "general", 0, []
        )
        assert result["grade"] in ("A", "B", "C", "D", "F")

    def test_interpretation_present(self):
        result = compute_ats_score(
            "Python developer with 5 years experience",
            "python_developer", "technical", 5.0, ["python"]
        )
        assert "interpretation" in result
        assert isinstance(result["interpretation"], str)

    def test_different_fields_produce_different_scores(self):
        text = "Python machine learning data analysis pandas sklearn tensorflow deep learning neural networks"
        ds = compute_ats_score(text, "data_scientist", "data_science", 3.0, ["python", "pandas", "sklearn"])
        fe = compute_ats_score(text, "frontend_developer", "technical", 3.0, ["python"])
        # Data scientist should score higher for this ML-heavy text
        assert ds["keyword_score"] != fe["keyword_score"]
