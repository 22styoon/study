from __future__ import annotations
from app.services.validation import validate_document

def validate_grading_result(result: dict) -> dict:
    validate_document(result, "grading.schema.json")
    for problem in result["problems"]:
        if problem["score"] > problem["max_score"]:
            raise ValueError(f"{problem['problem_id']}: score cannot exceed max_score")
    if result["requires_transcription_review"] and result["grading_status"] == "graded":
        raise ValueError("transcription review가 필요한 결과를 graded로 확정할 수 없습니다.")
    return result

def total_score(result: dict) -> float:
    validate_grading_result(result)
    return sum(problem["score"] for problem in result["problems"])
