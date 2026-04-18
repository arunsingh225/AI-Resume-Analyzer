"""
Unit tests for the resume parser module.
Tests cover: text cleaning, email/phone extraction, experience parsing, level detection.
"""
import pytest
from app.services.parser import (
    clean_text, extract_name, extract_email, extract_phone,
    extract_years_experience, check_formatting
)
from app.constants import determine_level


class TestCleanText:
    def test_removes_excess_whitespace(self):
        assert "hello world" in clean_text("hello     world")

    def test_normalizes_newlines(self):
        result = clean_text("line1\r\nline2\rline3")
        assert "\r" not in result

    def test_strips_leading_trailing(self):
        assert clean_text("  hello  ") == "hello"

    def test_preserves_special_chars(self):
        result = clean_text("C++ and C# developer")
        assert "C" in result


class TestExtractEmail:
    def test_standard_email(self):
        assert extract_email("Contact: john@gmail.com for details") == "john@gmail.com"

    def test_email_with_dots(self):
        assert extract_email("john.doe@company.co.uk") == "john.doe@company.co.uk"

    def test_no_email(self):
        assert extract_email("No email address here") == ""

    def test_email_in_resume_context(self):
        text = "John Doe\njohn.doe@example.com | +91 9876543210"
        assert extract_email(text) == "john.doe@example.com"


class TestExtractPhone:
    def test_indian_phone(self):
        result = extract_phone("+91 9876543210")
        assert "9876543210" in result

    def test_us_phone(self):
        result = extract_phone("(555) 123-4567")
        assert result != ""

    def test_no_phone(self):
        assert extract_phone("No phone number here") == ""


class TestExtractYearsExperience:
    def test_explicit_years(self):
        assert extract_years_experience("5 years of experience in software") == 5.0

    def test_years_with_plus(self):
        result = extract_years_experience("3+ years of experience")
        assert result == 3.0

    def test_months_to_years(self):
        result = extract_years_experience("18 months experience")
        assert result == 1.5

    def test_fresher_zero(self):
        result = extract_years_experience("Fresh graduate seeking opportunity in tech")
        assert result == 0.0

    def test_date_range(self):
        result = extract_years_experience("Software Engineer 2020 - 2024")
        assert result >= 3.0

    def test_experience_of_pattern(self):
        result = extract_years_experience("experience of 7 years in management")
        assert result == 7.0


class TestDetermineLevel:
    def test_fresher(self):
        assert determine_level(0) == "fresher"
        assert determine_level(0.5) == "fresher"

    def test_junior(self):
        assert determine_level(1) == "junior"
        assert determine_level(3) == "junior"

    def test_mid(self):
        assert determine_level(4) == "mid"
        assert determine_level(7) == "mid"

    def test_senior(self):
        assert determine_level(9) == "senior"
        assert determine_level(15) == "senior"


class TestCheckFormatting:
    def test_well_formatted_resume(self):
        text = """
        John Doe
        john@email.com | +91 9876543210
        linkedin.com/in/johndoe | github.com/johndoe

        • Developed a web application using React
        • Built REST APIs with FastAPI
        • Improved performance by 35%

        Education: B.Tech CS, 2022
        """
        result = check_formatting(text)
        assert "score" in result
        assert "checks" in result
        assert result["checks"]["has_email"] is True
        assert result["checks"]["has_bullets"] is True

    def test_minimal_resume(self):
        text = "John Doe developer"
        result = check_formatting(text)
        assert result["score"] < 50
        assert result["checks"]["has_email"] is False

    def test_scoring_bounds(self):
        text = "x" * 100
        result = check_formatting(text)
        assert 0 <= result["score"] <= 100


class TestExtractName:
    def test_standard_name(self):
        text = "John Doe\njohn@email.com\nSkills: Python"
        assert extract_name(text) == "John Doe"

    def test_three_word_name(self):
        text = "John Michael Doe\njohn@email.com"
        assert extract_name(text) == "John Michael Doe"

    def test_fallback_candidate(self):
        text = "12345\njohn@email.com\nskills: python"
        assert extract_name(text) == "Candidate"
