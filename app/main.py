from __future__ import annotations
from datetime import date
from pathlib import Path
from fastapi import Body, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.db import connection, init_db
from app.services.attendance import start_session
from app.services.submissions import receive_file
from app.services.lessons import validate_lesson
from app.services.grading import total_score, validate_grading_result
from app.services.proofs import submit_proof

app = FastAPI(title="Math Study System")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

@app.on_event("startup")
def startup() -> None:
    init_db()
    (Path(__file__).parent.parent / "data" / "inbox").mkdir(parents=True, exist_ok=True)

def dashboard_context(request: Request):
    today = date.today().isoformat()
    with connection() as conn:
        assignments = [dict(r) for r in conn.execute("SELECT * FROM assignments ORDER BY deadline_at").fetchall()]
        sessions = [dict(r) for r in conn.execute("SELECT * FROM sessions WHERE study_date=? ORDER BY id DESC LIMIT 1", (today,)).fetchall()]
        submissions = [dict(r) for r in conn.execute("SELECT * FROM submissions ORDER BY received_at DESC").fetchall()]
        topics = [dict(r) for r in conn.execute("SELECT * FROM topics ORDER BY subject, kind DESC, id").fetchall()]
        proofs = [dict(r) for r in conn.execute("SELECT * FROM proofs ORDER BY submitted_at DESC").fetchall()]
    return {"request": request, "today": today, "assignments": assignments, "session": sessions[0] if sessions else None, "submissions": submissions, "topics": topics, "proofs": proofs}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context=dashboard_context(request))

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.post("/sessions/start")
def begin_session(study_date: str = Form(...)):
    start_session(study_date)
    return RedirectResponse("/", status_code=303)

@app.post("/submissions")
async def upload_submission(assignment_id: str = Form(...), file: UploadFile = File(...)):
    safe_name = Path(file.filename or "upload").name
    inbox = Path(__file__).parent.parent / "data" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    source = inbox / safe_name
    source.write_bytes(await file.read())
    try:
        receive_file(assignment_id, source)
    except ValueError:
        return RedirectResponse("/?error=invalid", status_code=303)
    return RedirectResponse("/", status_code=303)

@app.post("/proofs")
def upload_proof(topic_id: str = Form(...), proof_text: str = Form(""), proof_image_data: str = Form("")):
    try:
        submit_proof(topic_id, proof_text, proof_image_data or None)
    except ValueError:
        return RedirectResponse("/?proof_error=invalid", status_code=303)
    return RedirectResponse("/?proof_submitted=1", status_code=303)

@app.post("/api/lessons/validate")
def validate_lesson_endpoint(lesson: dict = Body(...)):
    try:
        validate_lesson(lesson)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"valid": True, "problem_count": len(lesson["problems"])}

@app.post("/api/grades/validate")
def validate_grade_endpoint(result: dict = Body(...)):
    try:
        validate_grading_result(result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"valid": True, "total_score": total_score(result)}
