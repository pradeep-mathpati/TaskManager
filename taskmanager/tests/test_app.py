"""
Unit tests for Task Manager API
Run with: python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json
import app as application


@pytest.fixture
def client():
    application.app.config["TESTING"] = True
    # Reset tasks before each test
    application.tasks.clear()
    application.tasks.extend([
        {"id": 1, "title": "Test task one", "status": "pending", "priority": "high", "created_at": "2026-08-01"},
        {"id": 2, "title": "Test task two", "status": "done", "priority": "low", "created_at": "2026-08-02"},
    ])
    application.next_id = 3
    with application.app.test_client() as c:
        yield c


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


# ── GET all tasks ─────────────────────────────────────────────────────────────

def test_get_all_tasks(client):
    r = client.get("/api/tasks")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["count"] == 2
    assert len(data["tasks"]) == 2


def test_get_tasks_filtered_by_status(client):
    r = client.get("/api/tasks?status=pending")
    data = json.loads(r.data)
    assert data["count"] == 1
    assert data["tasks"][0]["status"] == "pending"


# ── GET single task ───────────────────────────────────────────────────────────

def test_get_single_task(client):
    r = client.get("/api/tasks/1")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["id"] == 1
    assert data["title"] == "Test task one"


def test_get_task_not_found(client):
    r = client.get("/api/tasks/999")
    assert r.status_code == 404


# ── POST create task ──────────────────────────────────────────────────────────

def test_create_task(client):
    payload = {"title": "New task from test", "priority": "medium"}
    r = client.post("/api/tasks", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 201
    data = json.loads(r.data)
    assert data["title"] == "New task from test"
    assert data["status"] == "pending"
    assert data["id"] == 3


def test_create_task_missing_title(client):
    r = client.post("/api/tasks", data=json.dumps({}), content_type="application/json")
    assert r.status_code == 400
    data = json.loads(r.data)
    assert "error" in data


# ── PUT update task ───────────────────────────────────────────────────────────

def test_update_task_status(client):
    payload = {"status": "done"}
    r = client.put("/api/tasks/1", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["status"] == "done"


def test_update_task_not_found(client):
    r = client.put("/api/tasks/999", data=json.dumps({"status": "done"}), content_type="application/json")
    assert r.status_code == 404


# ── DELETE task ───────────────────────────────────────────────────────────────

def test_delete_task(client):
    r = client.delete("/api/tasks/1")
    assert r.status_code == 200
    # Verify it's gone
    r2 = client.get("/api/tasks/1")
    assert r2.status_code == 404


def test_delete_task_not_found(client):
    r = client.delete("/api/tasks/999")
    assert r.status_code == 404


# ── Web UI ────────────────────────────────────────────────────────────────────

def test_homepage_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Task Manager" in r.data


def test_add_task_via_form(client):
    r = client.post("/add", data={"title": "UI form task", "priority": "high"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"UI form task" in r.data
