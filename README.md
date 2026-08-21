# Task Manager — Python Demo App.

A simple Python Flask web application built for the **Tricentis AI Workspace pipeline demo**.  
Has both a **web UI** and a **REST API** — perfect for Tosca (UI testing) and NeoLoad (API performance testing).

---

## Run locally (2 commands)

```bash
pip install flask
python app.py
```

Open http://localhost:5100 in your browser.

---

## Run with Docker

```bash
docker build -t task-manager .
docker run -p 5000:5000 task-manager
```

---

## Run tests

```bash
pip install flask pytest
python -m pytest tests/ -v
```

---

## Web UI test scenarios (for Tosca)

| Scenario | URL | Steps |
|---|---|---|
| View all tasks | `GET /` | Open homepage, verify task list loads |
| Add a task | `POST /add` | Fill form, submit, verify task appears |
| Complete a task | `GET /complete/:id` | Click Done, verify status changes |
| Delete a task | `GET /delete/:id` | Click Delete, verify task removed |

---

## REST API endpoints (for NeoLoad)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check — always returns 200 |
| GET | `/api/tasks` | List all tasks |
| GET | `/api/tasks?status=pending` | Filter by status |
| GET | `/api/tasks/:id` | Get single task |
| POST | `/api/tasks` | Create task (JSON body) |
| PUT | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |

### Example API calls

```bash
# Health check
curl http://localhost:5000/api/health

# Get all tasks
curl http://localhost:5000/api/tasks

# Create a task
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New task", "priority": "high"}'

# Update a task
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Delete a task
curl -X DELETE http://localhost:5000/api/tasks/1
```

---

## How to trigger the pipeline (after GitHub setup)

1. Edit this file (`README.md`) — add a line, change the date, anything
2. Commit to the `develop` branch
3. Open a Pull Request: `develop` → `main`
4. Merge the PR
5. Tricentis AI Workspace detects the merge and fires the full pipeline automatically

---

## Project structure

```
taskmanager/
├── app.py              ← Flask app (web UI + REST API)
├── requirements.txt    ← Just needs flask
├── Dockerfile          ← Run with Docker in 1 command
├── README.md           ← This file (also your pipeline trigger)
├── templates/
│   └── index.html      ← Web UI
└── tests/
    └── test_app.py     ← 14 unit tests covering all endpoints
```

---

## Pipeline trigger log

| Date | Change | Run |
|---|---|---|
| 2026-08-03 | Initial setup | Run 1 |
