from __future__ import annotations
import json
from pathlib import Path
from app.services.validation import validate_document

def validate_lesson(lesson: dict) -> dict:
    validate_document(lesson, "lesson.schema.json")
    return lesson

def save_lesson(lesson: dict, destination: Path) -> Path:
    validate_lesson(lesson)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination
