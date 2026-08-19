from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import json, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Simple in-memory store (no database needed - perfect for demo/testing)
tasks = [
    {"id": 1, "title": "Buy groceries", "status": "pending", "priority": "high", "created_at": "2026-08-01"},
    {"id": 2, "title": "Read a book", "status": "done", "priority": "low", "created_at": "2026-08-02"},
    {"id": 3, "title": "Write tests", "status": "pending", "priority": "medium", "created_at": "2026-08-03"},
]
next_id = 4

# In-memory user store (demo only - use a real user DB in production)
users = {
    "admin": generate_password_hash("admin123"),
}

# ── Auth helpers ───────────────────────────────────────────────────────────────

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

# ── Auth routes ────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_hash = users.get(username)
        if password_hash and check_password_hash(password_hash, password):
            session["username"] = username
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# ── Web UI routes ──────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    return render_template("index.html", tasks=tasks, username=session["username"])

@app.route("/add", methods=["POST"])
@login_required
def add_task():
    global next_id
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    if title:
        tasks.append({
            "id": next_id,
            "title": title,
            "status": "pending",
            "priority": priority,
            "created_at": datetime.today().strftime("%Y-%m-%d"),
        })
        next_id += 1
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
@login_required
def complete_task(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect(url_for("index"))

# ── REST API routes (for NeoLoad performance testing) ─────────────────────────

@app.route("/api/tasks", methods=["GET"])
def api_get_tasks():
    status = request.args.get("status")
    result = [t for t in tasks if t["status"] == status] if status else tasks
    return jsonify({"tasks": result, "count": len(result)})

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    global next_id
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    task = {
        "id": next_id,
        "title": title,
        "status": data.get("status", "pending"),
        "priority": data.get("priority", "medium"),
        "created_at": datetime.today().strftime("%Y-%m-%d"),
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json() or {}
    task.update({k: v for k, v in data.items() if k in ("title", "status", "priority")})
    return jsonify(task)

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == before:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": f"Task {task_id} deleted"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "task_count": len(tasks), "version": "1.0.0"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5100)
