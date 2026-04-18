"""
Unit tests for the JD matcher module.
"""
import pytest
from app.services.jd_matcher import (
    clean, tokenize, tfidf_similarity, keyword_overlap,
    skill_match, match_resume_to_jd
)


class TestClean:
    def test_lowercases(self):
        assert clean("Hello WORLD") == "hello world"

    def test_removes_special_chars(self):
        assert "python" in clean("Python, Java, & C++")


class TestTokenize:
    def test_removes_stopwords(self):
        tokens = tokenize("the quick brown fox and the lazy dog")
        assert "the" not in tokens
        assert "and" not in tokens

    def test_removes_short_words(self):
        tokens = tokenize("I am a AI developer")
        # Words with len <= 2 should be removed
        assert "am" not in tokens
        assert "developer" in tokens


class TestTfidfSimilarity:
    def test_similar_texts_high_score(self):
        score = tfidf_similarity(
            "python developer with django flask experience",
            "looking for python developer with django flask"
        )
        assert score > 0.3

    def test_different_texts_low_score(self):
        score = tfidf_similarity(
            "python developer with django flask experience",
            "accountant with GAAP IFRS financial reporting"
        )
        assert score < 0.3

    def test_empty_text_returns_zero(self):
        assert tfidf_similarity("", "") == 0.0


class TestKeywordOverlap:
    def test_found_and_missing(self):
        found, missing = keyword_overlap(
            "I know python and django",
            "We need python django flask"
        )
        assert "python" in found
        assert len(missing) > 0


class TestSkillMatch:
    def test_matches_technical_skills(self):
        matched, missing = skill_match(
            "Experience with python, react, docker, aws",
            "Looking for python, react, docker, aws, kubernetes"
        )
        assert "python" in matched
        assert "kubernetes" in missing

    def test_case_insensitive(self):
        matched, _ = skill_match("PYTHON and REACT", "python and react")
        assert "python" in matched


class TestMatchResumeToJD:
    def test_returns_all_fields(self):
        result = match_resume_to_jd(
            "Python developer with 5 years experience in Django, Flask, PostgreSQL, Docker, AWS",
            "Looking for Python developer with Django, Flask, cloud experience"
        )
        assert "match_percent" in result
        assert "tfidf_score" in result
        assert "keyword_overlap_pct" in result
        assert "skill_overlap_pct" in result
        assert "skills_matched" in result
        assert "skills_missing" in result
        assert "suggestions" in result
        assert "verdict" in result
        assert "match_method" in result

    def test_match_percent_in_bounds(self):
        result = match_resume_to_jd(
            "Python developer experienced in web development",
            "Looking for Python web developer"
        )
        assert 0 <= result["match_percent"] <= 100

    def test_high_match_for_similar(self):
        result = match_resume_to_jd(
            "Senior Python developer with 8 years experience in Django, Flask, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, CI/CD, Agile",
            "Senior Python developer needed. Must know Django, Flask, PostgreSQL, Docker, Kubernetes, AWS. CI/CD experience required."
        )
        assert result["match_percent"] >= 40

    def test_empty_text_raises(self):
        with pytest.raises(ValueError):
            match_resume_to_jd("", "some job description")

    def test_verdict_categories(self):
        result = match_resume_to_jd(
            "Python developer Django Flask",
            "Python developer Django Flask PostgreSQL"
        )
        assert result["verdict"] in [
            "Excellent match — apply immediately.",
            "Good match — minor tailoring needed.",
            "Moderate match — significant tailoring required.",
            "Low match — strongly consider rewriting your resume for this role."
        ]
