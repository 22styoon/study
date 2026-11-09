import pytest
from app.services.grading import total_score, validate_grading_result
from app.services.lessons import validate_lesson

def lesson():
    return {
        "subject": "Real Analysis", "study_date": "2026-11-09", "textbook": "Stoll, Introduction to Real Analysis, 3rd ed.",
        "section": "1.1 Sets and Operations on Sets", "prerequisites": ["basic logic"],
        "definitions": [{"term": "set", "statement": "A collection of objects."}], "theorems": [], "examples": ["Union and intersection"],
        "problems": [{"problem_id": "A-20261109-01", "prompt": "Prove the identity.", "max_score": 10, "solution_visibility": "after_submission"}],
        "estimated_minutes": 150, "submission_deadline": "2026-11-09T21:40:00+09:00", "solution_visibility": "hidden"
    }

def grade():
    return {"submission_id": "1", "grading_status": "needs_revision", "requires_transcription_review": False, "problems": [{"problem_id": "A-20261109-01", "score": 7, "max_score": 10, "independent_solution": True, "logical_gaps": ["missing justification"], "revision_required": True}]}

def test_lesson_schema_accepts_required_fields():
    assert validate_lesson(lesson())["subject"] == "Real Analysis"

def test_grade_schema_recalculates_total():
    assert total_score(grade()) == 7

def test_grade_rejects_score_above_maximum():
    invalid = grade()
    invalid["problems"][0]["score"] = 11
    with pytest.raises(ValueError, match="cannot exceed"):
        validate_grading_result(invalid)
