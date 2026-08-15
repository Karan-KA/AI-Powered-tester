from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class TestStep(BaseModel):
    action: str = Field(..., examples=["goto", "click", "fill", "assert_text", "screenshot"])
    selector: Optional[str] = None
    value: Optional[str] = None
    description: str
    optional: bool = False


class GenerateTestRequest(BaseModel):
    target_url: HttpUrl
    requirement: str = Field("", max_length=2000)
    session_id: Optional[int] = None


class SessionCreateRequest(BaseModel):
    target_url: HttpUrl
    title: str = Field("", max_length=180)


class SessionUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    target_url: str
    test_count: int = 0
    run_count: int = 0
    created_at: datetime
    updated_at: datetime


class TestCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: Optional[int] = None
    name: str
    target_url: str
    requirement: str
    steps: List[TestStep]
    expected_result: str
    generation_source: str = "fallback"
    intent_summary: str = ""
    created_at: datetime


class TestSuiteResponse(BaseModel):
    target_url: str
    page_title: str
    detected_features: List[str]
    tests: List[TestCaseResponse]


class RunRequest(BaseModel):
    test_case_id: int
    show_browser: bool = False


class TestRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_case_id: int
    status: str
    duration_ms: float
    summary: str
    error_summary: str
    logs: List[Dict[str, Any]]
    screenshots: List[str]
    started_at: datetime
    finished_at: Optional[datetime]


class AnalyticsResponse(BaseModel):
    total_cases: int
    total_runs: int
    pass_rate: float
    failed_runs: int
    warning_runs: int
    average_duration_ms: float
    recent_runs: List[TestRunResponse]
