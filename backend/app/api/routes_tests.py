from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TestCase, TestRun, TestSession
from app.schemas import (
    AnalyticsResponse,
    GenerateTestRequest,
    RunRequest,
    SessionCreateRequest,
    SessionResponse,
    SessionUpdateRequest,
    TestCaseResponse,
    TestRunResponse,
    TestStep,
    TestSuiteResponse,
)
from app.services.ai_service import generate_test_case, generate_test_suite
from app.services.executor_service import decode_json, encode_json, execute_steps
from app.services.llm_service import llm_status


router = APIRouter(prefix="/api", tags=["Web Test Automation"])


def _case_response(case: TestCase) -> TestCaseResponse:
    return TestCaseResponse(
        id=case.id,
        session_id=case.session_id,
        name=case.name,
        target_url=case.target_url,
        requirement=case.requirement,
        steps=decode_json(case.steps_json),
        expected_result=case.expected_result,
        generation_source=case.generation_source or "fallback",
        intent_summary=case.intent_summary or "",
        created_at=case.created_at,
    )


def _run_response(run: TestRun) -> TestRunResponse:
    return TestRunResponse(
        id=run.id,
        test_case_id=run.test_case_id,
        status=run.status,
        duration_ms=run.duration_ms,
        summary=run.summary,
        error_summary=run.error_summary,
        logs=decode_json(run.logs_json),
        screenshots=decode_json(run.screenshots_json),
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


def _steps_from_case(case: TestCase):
    return [step if isinstance(step, TestStep) else TestStep(**step) for step in decode_json(case.steps_json)]


def _save_generated_case(db: Session, generated: dict, session_id: int | None = None) -> TestCase:
    case = TestCase(
        session_id=session_id,
        name=generated["name"],
        target_url=generated["target_url"],
        requirement=generated["requirement"],
        steps_json=encode_json([step.model_dump() for step in generated["steps"]]),
        expected_result=generated["expected_result"],
        generation_source=generated.get("generation_source", "fallback"),
        intent_summary=generated.get("intent_summary", ""),
    )
    db.add(case)
    db.flush()
    return case


def _session_response(db: Session, session: TestSession) -> SessionResponse:
    cases = db.query(TestCase).filter(TestCase.session_id == session.id).all()
    case_ids = [case.id for case in cases]
    run_count = db.query(TestRun).filter(TestRun.test_case_id.in_(case_ids)).count() if case_ids else 0
    return SessionResponse(
        id=session.id,
        title=session.title,
        target_url=session.target_url,
        test_count=len(cases),
        run_count=run_count,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _session_for_request(db: Session, request: GenerateTestRequest) -> TestSession:
    target_url = str(request.target_url)
    if request.session_id:
        session = db.query(TestSession).filter(TestSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Test session not found")
        if session.target_url != target_url:
            raise HTTPException(status_code=400, detail="The session belongs to a different URL")
        return session

    title = request.requirement.strip() or f"Explore {target_url}"
    session = TestSession(title=title[:80], target_url=target_url)
    db.add(session)
    db.flush()
    return session


@router.get("/health")
def health():
    return {"status": "ok", "llm": llm_status()}


@router.post("/sessions", response_model=SessionResponse)
def create_session(request: SessionCreateRequest, db: Session = Depends(get_db)):
    target_url = str(request.target_url)
    title = request.title.strip() or f"New test for {target_url}"
    session = TestSession(title=title[:180], target_url=target_url)
    db.add(session)
    db.commit()
    db.refresh(session)
    return _session_response(db, session)


@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(TestSession).order_by(TestSession.updated_at.desc()).all()
    return [_session_response(db, session) for session in sessions]


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, request: SessionUpdateRequest, db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    session.title = request.title.strip()
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return _session_response(db, session)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    db.delete(session)
    db.commit()
    return {"message": "Test session deleted."}


@router.post("/tests/generate", response_model=TestCaseResponse)
@router.post("/generate-test", response_model=TestCaseResponse)
def generate_and_save_test(request: GenerateTestRequest, db: Session = Depends(get_db)):
    target_url = str(request.target_url)
    requirement = request.requirement.strip()
    generated = generate_test_case(target_url, requirement)
    session = _session_for_request(db, request)
    case = _save_generated_case(db, generated, session.id)
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return _case_response(case)


@router.post("/tests/generate-suite", response_model=TestSuiteResponse)
@router.post("/generate-suite", response_model=TestSuiteResponse)
def generate_and_save_suite(request: GenerateTestRequest, db: Session = Depends(get_db)):
    target_url = str(request.target_url)
    requirement = request.requirement.strip()
    suite = generate_test_suite(target_url, requirement)
    session = _session_for_request(db, request)
    saved_cases = [_save_generated_case(db, generated, session.id) for generated in suite["tests"]]
    session.updated_at = datetime.utcnow()
    db.commit()
    for case in saved_cases:
        db.refresh(case)

    return TestSuiteResponse(
        target_url=target_url,
        page_title=suite["page_title"],
        detected_features=suite["detected_features"],
        tests=[_case_response(case) for case in saved_cases],
    )


@router.get("/tests", response_model=List[TestCaseResponse])
def list_tests(session_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(TestCase)
    if session_id is not None:
        query = query.filter(TestCase.session_id == session_id)
    cases = query.order_by(TestCase.created_at.desc()).all()
    return [_case_response(case) for case in cases]


@router.delete("/tests")
def clear_tests(db: Session = Depends(get_db)):
    db.query(TestRun).delete()
    db.query(TestCase).delete()
    db.query(TestSession).delete()
    db.commit()
    return {"message": "All saved tests and runs were cleared."}


@router.get("/tests/{case_id}", response_model=TestCaseResponse)
def get_test(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return _case_response(case)


@router.post("/runs", response_model=TestRunResponse)
def run_test(request: RunRequest, db: Session = Depends(get_db)):
    case = db.query(TestCase).filter(TestCase.id == request.test_case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")

    run = TestRun(test_case_id=case.id, status="running", summary="Run started.")
    db.add(run)
    db.commit()
    db.refresh(run)

    status, summary, error_summary, logs, screenshots, duration_ms = execute_steps(
        run.id,
        case.target_url,
        _steps_from_case(case),
        show_browser=request.show_browser,
    )
    run.status = status
    run.summary = summary
    run.error_summary = error_summary
    run.logs_json = encode_json(logs)
    run.screenshots_json = encode_json(screenshots)
    run.duration_ms = duration_ms
    run.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(run)
    return _run_response(run)


@router.post("/execute-test/{test_case_id}", response_model=TestRunResponse)
def execute_test_by_id(test_case_id: int, show_browser: bool = False, db: Session = Depends(get_db)):
    return run_test(RunRequest(test_case_id=test_case_id, show_browser=show_browser), db)



@router.get("/runs", response_model=List[TestRunResponse])
def list_runs(session_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(TestRun)
    if session_id is not None:
        query = query.join(TestCase).filter(TestCase.session_id == session_id)
    runs = query.order_by(TestRun.started_at.desc()).all()
    return [_run_response(run) for run in runs]


@router.get("/runs/{run_id}", response_model=TestRunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_response(run)


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(db: Session = Depends(get_db)):
    total_cases = db.query(TestCase).count()
    runs = db.query(TestRun).order_by(TestRun.started_at.desc()).all()
    total_runs = len(runs)
    passed = len([run for run in runs if run.status == "passed"])
    failed = len([run for run in runs if run.status == "failed"])
    warnings = len([run for run in runs if run.status == "warning"])
    avg_duration = sum(run.duration_ms for run in runs) / total_runs if total_runs else 0
    return AnalyticsResponse(
        total_cases=total_cases,
        total_runs=total_runs,
        pass_rate=round((passed / total_runs) * 100, 2) if total_runs else 0,
        failed_runs=failed,
        warning_runs=warnings,
        average_duration_ms=round(avg_duration, 2),
        recent_runs=[_run_response(run) for run in runs[:8]],
    )
