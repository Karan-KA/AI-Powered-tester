import os
import tempfile
from pathlib import Path

test_root = Path(tempfile.gettempdir()) / "web_test_automation_tests"
test_root.mkdir(parents=True, exist_ok=True)
os.environ["DATA_DIR"] = str(test_root)
os.environ["ARTIFACTS_DIR"] = str(test_root / "artifacts")
os.environ["DATABASE_URL"] = f"sqlite:///{(test_root / 'web_test_automation_test.db').as_posix()}"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.schemas import TestStep as AutomationStep


client = TestClient(app)


def fake_generated_case(target_url, requirement):
    return {
        "name": "Generated test",
        "target_url": target_url,
        "requirement": requirement,
        "steps": [
            AutomationStep(action="goto", value=target_url, description="Open target."),
            AutomationStep(action="assert_title", description="Check title."),
        ],
        "expected_result": "The page loads.",
    }


def fake_generated_suite(target_url, requirement=""):
    return {
        "target_url": target_url,
        "page_title": "Example",
        "detected_features": ["page availability", "search"],
        "tests": [
            {
                "name": "Example - page availability",
                "target_url": target_url,
                "requirement": "Automatically generated from detected page functionality.",
                "steps": [AutomationStep(action="goto", value=target_url, description="Open target.")],
                "expected_result": "Page loads.",
            },
            {
                "name": "Example - search functionality",
                "target_url": target_url,
                "requirement": "Automatically generated from detected page functionality.",
                "steps": [
                    AutomationStep(action="goto", value=target_url, description="Open target."),
                    AutomationStep(action="fill", selector="input[type=search]", value="test", description="Search."),
                ],
                "expected_result": "Search works.",
            },
        ],
    }


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_test_case_and_list(monkeypatch):
    monkeypatch.setattr("app.api.routes_tests.generate_test_case", fake_generated_case)
    session = client.post(
        "/api/sessions",
        json={"target_url": "https://example.com", "title": "Example checks"},
    ).json()
    response = client.post(
        "/api/tests/generate",
        json={
            "target_url": "https://example.com",
            "requirement": "Check that the home page loads correctly and capture evidence.",
            "session_id": session["id"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["steps"][0]["action"] == "goto"

    list_response = client.get("/api/tests")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    repeated_response = client.post(
        "/api/tests/generate",
        json={
            "target_url": "https://example.com",
            "requirement": "Check that the home page loads correctly and capture evidence.",
            "session_id": session["id"],
        },
    )
    assert repeated_response.status_code == 200
    assert len(client.get(f"/api/tests?session_id={session['id']}").json()) == 2

    changed_prompt_response = client.post(
        "/api/tests/generate",
        json={
            "target_url": "https://example.com",
            "requirement": "Search for a different value.",
            "session_id": session["id"],
        },
    )
    assert changed_prompt_response.status_code == 200
    saved = client.get(f"/api/tests?session_id={session['id']}").json()
    assert len(saved) == 3
    assert saved[0]["requirement"] == "Search for a different value."


def test_generate_blank_requirement_is_allowed(monkeypatch):
    monkeypatch.setattr("app.api.routes_tests.generate_test_case", fake_generated_case)
    response = client.post(
        "/api/tests/generate",
        json={
            "target_url": "https://example.com",
            "requirement": "",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"]
    assert data["steps"][0]["action"] == "goto"


def test_clear_tests(monkeypatch):
    monkeypatch.setattr("app.api.routes_tests.generate_test_case", fake_generated_case)
    client.post(
        "/api/tests/generate",
        json={"target_url": "https://example.com", "requirement": ""},
    )
    response = client.delete("/api/tests")
    assert response.status_code == 200
    assert client.get("/api/tests").json() == []


def test_generate_suite_appends_to_session_history(monkeypatch):
    monkeypatch.setattr("app.api.routes_tests.generate_test_suite", fake_generated_suite)
    session = client.post(
        "/api/sessions",
        json={"target_url": "https://example.com", "title": "Suite history"},
    ).json()
    payload = {"target_url": "https://example.com", "requirement": "", "session_id": session["id"]}

    first = client.post("/api/tests/generate-suite", json=payload)
    second = client.post("/api/tests/generate-suite", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(second.json()["tests"]) == 2
    assert len(client.get(f"/api/tests?session_id={session['id']}").json()) == 4


def test_sessions_are_scoped_and_deletable(monkeypatch):
    monkeypatch.setattr("app.api.routes_tests.generate_test_case", fake_generated_case)
    first = client.post(
        "/api/sessions",
        json={"target_url": "https://example.com", "title": "Example"},
    ).json()
    second = client.post(
        "/api/sessions",
        json={"target_url": "https://openai.com", "title": "OpenAI"},
    ).json()

    client.post(
        "/api/tests/generate",
        json={"target_url": "https://example.com", "requirement": "Load page", "session_id": first["id"]},
    )

    assert len(client.get(f"/api/tests?session_id={first['id']}").json()) == 1
    assert client.get(f"/api/tests?session_id={second['id']}").json() == []
    assert client.delete(f"/api/sessions/{first['id']}").status_code == 200
    assert [item["id"] for item in client.get("/api/sessions").json()] == [second["id"]]


def test_analytics_empty_shape():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] == 0
    assert data["total_runs"] == 0
    assert data["recent_runs"] == []


def test_report_route_aliases(monkeypatch):
    monkeypatch.setattr("app.api.routes_tests.generate_test_case", fake_generated_case)
    monkeypatch.setattr("app.api.routes_tests.generate_test_suite", fake_generated_suite)
    
    # Test POST /api/generate-test
    res1 = client.post("/api/generate-test", json={"target_url": "https://example.com", "requirement": "Check page"})
    assert res1.status_code == 200
    case_id = res1.json()["id"]

    # Test POST /api/generate-suite
    res2 = client.post("/api/generate-suite", json={"target_url": "https://example.com", "requirement": ""})
    assert res2.status_code == 200
    assert len(res2.json()["tests"]) == 2

    # Mock execute_steps to test POST /api/execute-test/{case_id}
    monkeypatch.setattr(
        "app.api.routes_tests.execute_steps",
        lambda run_id, url, steps, show_browser=False: ("passed", "Run finished", "", [], ["/screenshots/sample.png"], 120.0)
    )
    res3 = client.post(f"/api/execute-test/{case_id}")
    assert res3.status_code == 200
    assert res3.json()["status"] == "passed"
    assert res3.json()["screenshots"] == ["/screenshots/sample.png"]

