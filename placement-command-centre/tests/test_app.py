import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def app_module(monkeypatch):
    import app as module
    with tempfile.TemporaryDirectory(dir=module.ROOT / "data", prefix=".test-") as temporary:
        monkeypatch.setattr(module, "DB_PATH", Path(temporary) / "placement.db")
        module.initialize()
        module.app.config.update(TESTING=True)
        yield module


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()


def csrf(client):
    response = client.get("/")
    assert response.status_code == 200
    return response.get_data(as_text=True).split('name="csrf-token" content="', 1)[1].split('"', 1)[0]


def test_today_is_idempotent_and_has_one_checklist(client, app_module):
    first = client.get("/api/today").get_json()
    app_module.initialize()
    second = client.get("/api/today").get_json()
    assert first["record"]["id"] == second["record"]["id"]
    assert len(second["tasks"]) == 10


def test_task_completion_persists_between_connections(client):
    token = csrf(client)
    task_id = client.get("/api/today").get_json()["tasks"][0]["id"]
    response = client.patch(f"/api/checklist/{task_id}", json={"done": True}, headers={"X-CSRF-Token": token})
    assert response.status_code == 200
    assert client.get("/api/today").get_json()["tasks"][0]["done"] == 1


def test_mutations_require_csrf(client):
    response = client.post("/api/entries/coding", json={"title": "An actual user entry"})
    assert response.status_code == 400


def test_entry_crud_and_validation(client):
    token = csrf(client)
    headers = {"X-CSRF-Token": token}
    invalid = client.post("/api/entries/coding", json={"title": " "}, headers=headers)
    assert invalid.status_code == 400
    created = client.post("/api/entries/coding", json={"title": "Array exercise", "status": "Solved"}, headers=headers)
    assert created.status_code == 201
    entry_id = created.get_json()["id"]
    changed = client.patch(f"/api/entries/{entry_id}", json={"status": "Needs Revision"}, headers=headers)
    assert changed.get_json()["status"] == "Needs Revision"
    assert client.delete(f"/api/entries/{entry_id}", headers=headers).status_code == 200
    assert client.get("/api/entries/coding").get_json() == []


def test_stats_only_count_saved_activity(client):
    stats = client.get("/api/stats").get_json()
    assert stats["solved"] == 0
    assert stats["applied"] == 0
    assert stats["xp"] == 0


def test_plan_start_setting_saves_and_backfills(client):
    token = csrf(client)
    response = client.patch("/api/settings", json={"plan_start": "2026-10-20"}, headers={"X-CSRF-Token": token})
    assert response.status_code == 200
    data = client.get("/api/today").get_json()
    assert data["day_number"] == 6
    assert len(data["history"]) >= 6


def test_source_pack_imports_templates_and_keeps_legacy_archived(client, app_module):
    assert len(client.get("/api/entries/questions").get_json()) == 126
    assert len(client.get("/api/entries/fundamentals").get_json()) == 18
    assert len(client.get("/api/entries/interview").get_json()) == 52
    assert len(client.get("/api/entries/projects").get_json()) == 15
    assert len(client.get("/api/curriculum/roadmap").get_json()) == 30
    assert len(client.get("/api/curriculum/starter").get_json()) == 11
    assert len(client.get("/api/curriculum/schedule").get_json()) == 15
    legacy = client.get("/api/legacy").get_json()
    assert len(legacy) == 87
    assert sum(row["status"] == "Done" for row in legacy) == 43
    assert client.get("/api/entries/jobs").get_json() == []
    assert client.get("/api/entries/revisions").get_json() == []
    first_count = len(client.get("/api/entries/questions").get_json())
    app_module.initialize()
    assert len(client.get("/api/entries/questions").get_json()) == first_count


def test_imported_starter_and_scorecard_logs_are_editable(client):
    token = csrf(client)
    headers = {"X-CSRF-Token": token}
    starter = client.get("/api/curriculum/starter").get_json()[0]
    assert client.patch(f"/api/curriculum/{starter['id']}", json={"completed": True}, headers=headers).status_code == 200
    result = client.patch("/api/quick-log", json={"coding_attempted": 2, "applications_submitted": 1, "speaking_minutes": 10, "core_cs_done": True}, headers=headers)
    assert result.status_code == 200
    assert result.get_json()["record"]["coding_attempted"] == 2
    assert result.get_json()["record"]["core_cs_done"] == 1
    assert client.get("/api/stats").get_json()["readiness"]["score"] is not None


def test_imported_schedule_preserves_college_and_sleep_times(client):
    schedule = client.get("/api/curriculum/schedule").get_json()
    college = next(item for item in schedule if item["title"] == "College")
    sleep = next(item for item in schedule if item["title"] == "Sleep")
    assert (college["start_time"], college["end_time"]) == (570, 990)
    assert sleep["start_time"] == 1320
