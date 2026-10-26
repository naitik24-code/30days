from __future__ import annotations

import json
import os
import csv
import re
import sqlite3
import secrets
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session


ROOT = Path(__file__).resolve().parent
# Vercel's filesystem is read-only except /tmp, so fall back to /tmp there.
# NOTE: /tmp is ephemeral; set TURSO_DATABASE_URL + TURSO_AUTH_TOKEN for real persistence.
_default_db = Path("/tmp/placement.db") if os.environ.get("VERCEL") else ROOT / "data" / "placement.db"
DB_PATH = Path(os.environ.get("PLACEMENT_DB", _default_db))
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "").strip()
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "").strip()
TASKS = ["Aptitude practice", "DSA and coding practice", "Core CS fundamentals", "SQL practice", "Portfolio project work", "Apply to relevant jobs", "LinkedIn networking", "Interview communication practice", "Revise previous coding questions", "End-of-day review"]
SECTIONS = {"practice": ["questions", "coding", "fundamentals", "interview", "revisions"], "career": ["jobs", "projects"], "progress": ["scorecard", "review", "achievements"], "library": ["guide", "cheatsheet", "rules", "tracker"]}


def today() -> date:
    return date.today()


@contextmanager
def connect():
    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        import turso_serverless

        url = TURSO_DATABASE_URL
        if url.startswith("libsql://"):
            url = "https://" + url[len("libsql://"):]
        db = turso_serverless.connect(url, auth_token=TURSO_AUTH_TOKEN)
        db.row_factory = turso_serverless.Row
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def read_csv(source: Path) -> list[dict[str, str]]:
    with source.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def csv_value(row: dict[str, str], label: str, default: str = "") -> str:
    target = re.sub(r"[^a-z0-9]", "", label.lower())
    for key, value in row.items():
        normalized = re.sub(r"[^a-z0-9]", "", key.lower())
        if normalized == target or normalized.startswith(target):
            return value or default
    return default


def time_options(value: str) -> list[int]:
    match = re.match(r"\s*(\d{1,2}):(\d{2})\s*(AM|PM)?", value, re.IGNORECASE)
    if not match:
        return []
    hour, minute = int(match.group(1)), int(match.group(2))
    period = (match.group(3) or "").upper()
    if minute > 59 or hour > 12 or (period and hour == 0):
        return []
    base = hour % 12 * 60 + minute
    if period == "AM":
        return [base]
    if period == "PM":
        return [base + 720]
    return sorted({base, base + 720})


def schedule_minutes(label: str, previous_end: int | None) -> tuple[int | None, int | None]:
    parts = re.split(r"\s*[–-]\s*", label.strip(), maxsplit=1)
    starts = time_options(parts[0])
    if not starts:
        return None, None
    ends = time_options(parts[1]) if len(parts) == 2 else []
    minimum = previous_end if previous_end is not None else 0
    candidates = [(start, end) for start in starts for end in ends if start >= minimum and end > start]
    if candidates:
        return min(candidates)
    eligible = [start for start in starts if start >= minimum]
    return (min(eligible), None) if eligible else (None, None)


def add_source_entry(db: sqlite3.Connection, kind: str, title: str, status: str, topic: str, notes: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    db.execute("INSERT INTO entries(kind,title,status,topic,notes,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", (kind, title[:180], status or "Not Started", topic[:100], notes[:2000], now, now))


def import_source_pack(db: sqlite3.Connection) -> None:
    pack = ROOT / "data" / "source_pack"
    if not pack.is_dir() or db.execute("SELECT 1 FROM app_meta WHERE key='source_pack_v1'").fetchone():
        return
    questions = read_csv(pack / "05_Master_Question_Tracker.csv")
    if not db.execute("SELECT 1 FROM entries WHERE kind='questions' LIMIT 1").fetchone():
        for row in questions:
            notes = "\n".join(value for value in (f"Question #{csv_value(row, 'No.')}", f"Mental model: {csv_value(row, 'Learning Tip / Mental Model')}", f"Mastery evidence: {csv_value(row, 'Proof of mastery')}", f"Confidence: {csv_value(row, 'Confidence')}", f"Revisit: {csv_value(row, 'Revisit')}") if value.split(": ",1)[-1].strip())
            add_source_entry(db, "questions", csv_value(row, "Question / Exercise"), csv_value(row, "Status", "Not Started"), csv_value(row, "Section"), notes)
    basics = read_csv(pack / "04_Basics_Learning_Path.csv")
    if not db.execute("SELECT 1 FROM entries WHERE kind='fundamentals' LIMIT 1").fetchone():
        for row in basics:
            notes = "\n".join((f"Self-check: {csv_value(row, 'You must be able to answer')}", f"Ready when: {csv_value(row, 'You are ready to move on when')}", f"Common trap: {csv_value(row, 'Common trap')}"))
            add_source_entry(db, "fundamentals", csv_value(row, "Concept"), "Not Started", f"Learning path · step {csv_value(row, 'Order')}", notes)
    interviews = read_csv(pack / "06_Interview_Question_Bank.csv")
    if not db.execute("SELECT 1 FROM entries WHERE kind='interview' LIMIT 1").fetchone():
        for row in interviews:
            notes = "\n".join(value for value in (f"Strong answer includes: {csv_value(row, 'What a strong answer includes')}", f"Practice notes: {csv_value(row, 'Notes / example')}", f"Confidence: {csv_value(row, 'Confidence')}") if value.split(": ",1)[-1].strip())
            add_source_entry(db, "interview", csv_value(row, "Question / prompt"), csv_value(row, "Practice status", "Not Started"), csv_value(row, "Category"), notes)
    projects = read_csv(pack / "07_Project_Upgrade_Board.csv")
    if not db.execute("SELECT 1 FROM entries WHERE kind='projects' LIMIT 1").fetchone():
        for row in projects:
            notes = "\n".join(value for value in (f"Priority: {csv_value(row, 'Priority')}", f"Done when: {csv_value(row, 'Definition of done')}", f"Next action: {csv_value(row, 'Next action')}", f"Risk: {csv_value(row, 'Risk / limitation')}") if value.split(": ",1)[-1].strip())
            add_source_entry(db, "projects", csv_value(row, "Audit question / task"), csv_value(row, "Status", "Not Started"), f"{csv_value(row, 'Project')} / {csv_value(row, 'Workstream')}", notes)
    roadmap = read_csv(pack / "02_30_Day_Roadmap.csv")
    for row in roadmap:
        ordinal_text = csv_value(row, "Day")
        if not ordinal_text.isdigit():
            content = "\n".join(f"{key}: {value}" for key, value in row.items() if key != "Day" and value.strip())
            db.execute("INSERT OR IGNORE INTO curriculum(kind,ordinal,title,content,source) VALUES('rules',1,?,?,?)", ("Mastery rule", content, "02_30_Day_Roadmap.csv"))
            db.execute("INSERT OR IGNORE INTO resources(kind,title,content,source) VALUES('mastery_rule',?,?,?)", ("Mastery rule", content, "02_30_Day_Roadmap.csv"))
            continue
        ordinal = int(ordinal_text)
        content = "\n".join(f"{key}: {value}" for key, value in row.items() if key != "Day" and value.strip())
        db.execute("INSERT OR IGNORE INTO curriculum(kind,ordinal,title,content,source) VALUES('roadmap',?,?,?,?)", (ordinal, f"Day {ordinal}", content, "02_30_Day_Roadmap.csv"))
    starter = read_csv(pack / "03_Day_1_Starter.csv")
    for index, row in enumerate(starter, 1):
        done = csv_value(row, "Done?").strip().lower() in {"true", "yes", "done", "1", "x"}
        content = "\n".join(value for value in (csv_value(row, "How to do it"), csv_value(row, "Evidence / notes")) if value.strip())
        db.execute("INSERT OR IGNORE INTO curriculum(kind,ordinal,title,content,source,completed) VALUES('starter',?,?,?,?,?)", (index, csv_value(row, "Task", f"Step {index}"), content, "03_Day_1_Starter.csv", int(done)))
    schedule = read_csv(pack / "01_Daily_Operating_System.csv")
    last_end = None
    for index, row in enumerate(schedule, 1):
        start_minute, end_minute = schedule_minutes(csv_value(row, "Time"), last_end)
        if end_minute is not None:
            last_end = end_minute
        content = "\n".join(f"{key}: {value}" for key, value in row.items() if key not in {"Time", "Block"} and value.strip() and value.strip() != "—")
        db.execute("INSERT OR IGNORE INTO curriculum(kind,ordinal,title,content,source,start_time,end_time) VALUES('schedule',?,?,?,?,?,?)", (index, csv_value(row, "Block", f"Block {index}"), content, "01_Daily_Operating_System.csv", start_minute, end_minute))
    legacy = read_csv(pack / "12_Original_Tracker_Backup.csv")
    for index, row in enumerate(legacy, 1):
        db.execute("INSERT OR IGNORE INTO legacy_records(source_id,day,section,title,priority,status,reference) VALUES(?,?,?,?,?,?,?)", (index, csv_value(row, "Day"), csv_value(row, "Section"), csv_value(row, "Question / Topic"), csv_value(row, "Priority"), csv_value(row, "Status"), csv_value(row, "PDF / Day")))
    markdown_files = {"00_START_HERE_Dashboard.md": "start", "13_Coding_Learning_Guide.md": "learning_guide", "14_Coding_Cheat_Sheet.md": "cheat_sheet", "15_Notion_Property_Setup.md": "property_setup"}
    for filename, kind in markdown_files.items():
        source = pack / filename
        db.execute("INSERT OR IGNORE INTO resources(kind,title,content,source) VALUES(?,?,?,?)", (kind, source.stem.replace("_", " "), source.read_text(encoding="utf-8-sig"), filename))
    template_files = {"08_Job_Application_Tracker.csv": "job_template", "09_Daily_Scorecard.csv": "scorecard_template", "10_Spaced_Revision_Tracker.csv": "revision_template", "11_Weekly_Review.csv": "weekly_template"}
    for filename, kind in template_files.items():
        source = pack / filename
        rows = read_csv(source)
        summary = f"{len(rows)} starter rows; no activity has been imported." if rows else "This source tracker has no rows yet. Add real records as they happen."
        db.execute("INSERT OR IGNORE INTO resources(kind,title,content,source) VALUES(?,?,?,?)", (kind, source.stem.replace("_", " "), summary, filename))
    done_count = sum(row.get("Status", "").strip().lower() == "done" for row in legacy)
    db.execute("INSERT OR IGNORE INTO resources(kind,title,content,source) VALUES('legacy_archive',?,?,?)", ("Original tracker archive", f"{len(legacy)} source rows retained for reference. {done_count} were marked Done and remain archived; they do not count toward current placement progress.", "12_Original_Tracker_Backup.csv"))
    db.execute("INSERT INTO app_meta(key,value) VALUES('source_pack_v1',?)", (datetime.now().isoformat(timespec="seconds"),))


def _already_initialized(db) -> bool:
    """One cheap query: skip the heavy setup when the DB is already fully prepared (big win over remote Turso)."""
    try:
        row = db.execute(
            "SELECT (SELECT MAX(version) FROM schema_version),"
            " (SELECT COUNT(*) FROM app_meta WHERE key='source_pack_v1'),"
            " (SELECT COUNT(*) FROM checklist c JOIN daily_records d ON d.id=c.day_id WHERE d.date=?)",
            (today().isoformat(),),
        ).fetchone()
        return bool(row and (row[0] or 0) >= 3 and row[1] and row[2] >= len(TASKS))
    except Exception:
        return False


def initialize(force: bool = False) -> None:
    with connect() as db:
        if not force and _already_initialized(db):
            return
        db.executescript("""
        CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
        INSERT INTO schema_version SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM schema_version);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS daily_records(id INTEGER PRIMARY KEY, date TEXT UNIQUE NOT NULL, sleep REAL, energy INTEGER CHECK(energy BETWEEN 1 AND 5), aptitude INTEGER, reflection TEXT DEFAULT '', light_day INTEGER NOT NULL DEFAULT 0, aptitude_accuracy REAL, coding_attempted INTEGER NOT NULL DEFAULT 0, coding_solved INTEGER NOT NULL DEFAULT 0, core_cs_done INTEGER NOT NULL DEFAULT 0, project_deliverable TEXT DEFAULT '', applications_submitted INTEGER NOT NULL DEFAULT 0, linkedin_requests INTEGER NOT NULL DEFAULT 0, speaking_minutes INTEGER NOT NULL DEFAULT 0, instagram_task TEXT DEFAULT '', blocker TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS checklist(id INTEGER PRIMARY KEY, day_id INTEGER NOT NULL REFERENCES daily_records(id) ON DELETE CASCADE, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)), UNIQUE(day_id,title));
        CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Not Started', topic TEXT DEFAULT '', notes TEXT DEFAULT '', due_date TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS entries_kind_status ON entries(kind,status);
        CREATE TABLE IF NOT EXISTS focus_sessions(id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, minutes INTEGER NOT NULL, subject TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS weekly_reviews(id INTEGER PRIMARY KEY, week_start TEXT UNIQUE NOT NULL, focus TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS app_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS curriculum(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, ordinal INTEGER NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT '', completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)), start_time INTEGER, end_time INTEGER, UNIQUE(kind,ordinal));
        CREATE TABLE IF NOT EXISTS resources(kind TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, source TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS legacy_records(id INTEGER PRIMARY KEY, source_id INTEGER UNIQUE NOT NULL, day TEXT NOT NULL, section TEXT NOT NULL, title TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL, reference TEXT NOT NULL);
        INSERT INTO schema_version SELECT 2 WHERE NOT EXISTS(SELECT 1 FROM schema_version WHERE version>=2);
        """)
        columns = {row["name"] for row in db.execute("PRAGMA table_info(daily_records)")}
        for name, definition in (("aptitude_accuracy", "REAL"), ("coding_attempted", "INTEGER NOT NULL DEFAULT 0"), ("coding_solved", "INTEGER NOT NULL DEFAULT 0"), ("core_cs_done", "INTEGER NOT NULL DEFAULT 0"), ("project_deliverable", "TEXT DEFAULT ''"), ("applications_submitted", "INTEGER NOT NULL DEFAULT 0"), ("linkedin_requests", "INTEGER NOT NULL DEFAULT 0"), ("speaking_minutes", "INTEGER NOT NULL DEFAULT 0"), ("instagram_task", "TEXT DEFAULT ''"), ("blocker", "TEXT DEFAULT ''")):
            if name not in columns:
                db.execute(f"ALTER TABLE daily_records ADD COLUMN {name} {definition}")
        db.execute("UPDATE schema_version SET version=3 WHERE version<3")
        start = db.execute("SELECT value FROM settings WHERE key='plan_start'").fetchone()
        if not start:
            db.execute("INSERT INTO settings(key,value) VALUES('plan_start',?)", (today().isoformat(),))
        db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('theme','dark')")
        db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('streak_threshold','6')")
        plan_start = date.fromisoformat(db.execute("SELECT value FROM settings WHERE key='plan_start'").fetchone()[0])
        cursor = max(plan_start, today() - timedelta(days=29))
        have = {r[0] for r in db.execute("SELECT d.date FROM daily_records d JOIN checklist c ON c.day_id=d.id GROUP BY d.id HAVING COUNT(c.id)>=?", (len(TASKS),))}
        while cursor <= today():
            if cursor.isoformat() in have:
                cursor += timedelta(days=1)
                continue
            db.execute("INSERT OR IGNORE INTO daily_records(date) VALUES(?)", (cursor.isoformat(),))
            day_id = db.execute("SELECT id FROM daily_records WHERE date=?", (cursor.isoformat(),)).fetchone()[0]
            for task in TASKS:
                db.execute("INSERT OR IGNORE INTO checklist(day_id,title) VALUES(?,?)", (day_id, task))
            cursor += timedelta(days=1)
        import_source_pack(db)
        mastery_rule = db.execute("SELECT content,source FROM curriculum WHERE kind='rules' AND ordinal=1").fetchone()
        if mastery_rule:
            db.execute("INSERT OR IGNORE INTO resources(kind,title,content,source) VALUES('mastery_rule',?,?,?)", ("Mastery rule", mastery_rule["content"], mastery_rule["source"]))


def record_for(db: sqlite3.Connection, day: date | None = None) -> sqlite3.Row:
    return db.execute("SELECT * FROM daily_records WHERE date=?", ((day or today()).isoformat(),)).fetchone()


def payload(db: sqlite3.Connection, day: date | None = None) -> dict:
    current = day or today()
    record = record_for(db, current)
    tasks = [dict(row) for row in db.execute("SELECT id,title,done FROM checklist WHERE day_id=? ORDER BY id", (record["id"],))]
    history = [dict(row) for row in db.execute("SELECT d.date,COUNT(c.id) total,SUM(c.done) done,d.aptitude,d.aptitude_accuracy,d.coding_attempted,d.coding_solved,d.applications_submitted,d.speaking_minutes,d.sleep,d.energy FROM daily_records d LEFT JOIN checklist c ON c.day_id=d.id WHERE d.date BETWEEN ? AND ? GROUP BY d.id ORDER BY d.date", ((current - timedelta(days=29)).isoformat(), current.isoformat()))]
    settings = {r["key"]: r["value"] for r in db.execute("SELECT key,value FROM settings")}
    day_number = max(0, min(30, (current - date.fromisoformat(settings["plan_start"])).days + 1))
    rows = db.execute("SELECT * FROM curriculum WHERE (kind='roadmap' AND ordinal=?) OR kind='starter' ORDER BY ordinal", (day_number,)).fetchall()
    roadmap = next((r for r in rows if r["kind"] == "roadmap"), None)
    starter = [{k: r[k] for k in ("id", "ordinal", "title", "content", "completed")} for r in rows if r["kind"] == "starter"]
    return {"date": current.isoformat(), "record": dict(record), "tasks": tasks, "history": history, "day_number": day_number, "roadmap": dict(roadmap) if roadmap else None, "starter": starter, "settings": settings}


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.secret_key = os.environ.get("PLACEMENT_SECRET", "placement_command_centre_secure_fallback_key_2026")


@app.before_request
def require_csrf_for_changes():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        token = session.get("csrf_token")
        if not token or request.headers.get("X-CSRF-Token") != token:
            return jsonify(error="Refresh the page and try again."), 400
    elif request.method == "GET" and "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)


@app.get("/")
def home():
    token = f'<meta name="csrf-token" content="{session["csrf_token"]}">'
    page = render_template("index.html", csrf_meta=token)
    if 'name="csrf-token"' not in page:
        page = page.replace('<meta name="theme-color" content="#0a0f1f">', f'<meta name="theme-color" content="#0a0f1f">{token}')
    return page


@app.get("/api/today")
def api_today():
    with connect() as db:
        return jsonify(payload(db))


@app.get("/api/curriculum/<kind>")
def get_curriculum(kind: str):
    if kind not in {"schedule", "roadmap", "starter"}:
        return jsonify(error="Unknown guide list."), 404
    with connect() as db:
        rows = db.execute("SELECT * FROM curriculum WHERE kind=? ORDER BY ordinal", (kind,)).fetchall()
        return jsonify([dict(row) for row in rows])


@app.patch("/api/curriculum/<int:item_id>")
def update_curriculum(item_id: int):
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("completed"), bool):
        return jsonify(error="Completion must be true or false."), 400
    with connect() as db:
        cursor = db.execute("UPDATE curriculum SET completed=? WHERE id=? AND kind='starter'", (int(data["completed"]), item_id))
        if not cursor.rowcount:
            return jsonify(error="Setup step not found."), 404
    return jsonify(ok=True)


@app.get("/api/resources")
def get_resources():
    with connect() as db:
        return jsonify([dict(row) for row in db.execute("SELECT kind,title,content,source FROM resources ORDER BY kind")])


@app.get("/api/legacy")
def get_legacy_records():
    with connect() as db:
        rows = db.execute("SELECT source_id,day,section,title,priority,status,reference FROM legacy_records ORDER BY source_id").fetchall()
        return jsonify([dict(row) for row in rows])


@app.get("/api/entries/<kind>")
def list_entries(kind: str):
    if kind not in {value for group in SECTIONS.values() for value in group}:
        return jsonify(error="Unknown list"), 404
    query = request.args.get("q", "").strip()
    with connect() as db:
        rows = db.execute("SELECT * FROM entries WHERE kind=? AND (title LIKE ? OR topic LIKE ? OR notes LIKE ?) ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,due_date,CASE WHEN kind IN ('questions','fundamentals','interview','projects') THEN id END ASC,id DESC", (kind, f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
        return jsonify([dict(row) for row in rows])


@app.post("/api/entries/<kind>")
def create_entry(kind: str):
    if kind not in {value for group in SECTIONS.values() for value in group}:
        return jsonify(error="Unknown list"), 404
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title or len(title) > 180:
        return jsonify(error="Add a title (up to 180 characters)."), 400
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as db:
        cur = db.execute("INSERT INTO entries(kind,title,status,topic,notes,due_date,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)", (kind, title, str(data.get("status", "Not Started")), str(data.get("topic", ""))[:100], str(data.get("notes", ""))[:2000], data.get("due_date") or None, now, now))
        return jsonify(dict(db.execute("SELECT * FROM entries WHERE id=?", (cur.lastrowid,)).fetchone())), 201


@app.patch("/api/entries/<int:entry_id>")
def update_entry(entry_id: int):
    data = request.get_json(silent=True) or {}
    allowed = {"title", "status", "topic", "notes", "due_date"}
    values = {key: data[key] for key in allowed if key in data}
    if not values:
        return jsonify(error="No changes supplied."), 400
    if "title" in values and not str(values["title"]).strip():
        return jsonify(error="Title cannot be empty."), 400
    with connect() as db:
        if not db.execute("SELECT id FROM entries WHERE id=?", (entry_id,)).fetchone():
            return jsonify(error="Record not found."), 404
        values["updated_at"] = datetime.now().isoformat(timespec="seconds")
        db.execute("UPDATE entries SET " + ",".join(f"{key}=?" for key in values) + " WHERE id=?", (*values.values(), entry_id))
        return jsonify(dict(db.execute("SELECT * FROM entries WHERE id=?", (entry_id,)).fetchone()))


@app.delete("/api/entries/<int:entry_id>")
def delete_entry(entry_id: int):
    with connect() as db:
        cur = db.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        if not cur.rowcount:
            return jsonify(error="Record not found."), 404
    return jsonify(ok=True)


@app.patch("/api/checklist/<int:task_id>")
def toggle_task(task_id: int):
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("done"), bool):
        return jsonify(error="Completion must be true or false."), 400
    with connect() as db:
        cur = db.execute("UPDATE checklist SET done=? WHERE id=?", (int(data["done"]), task_id))
        if not cur.rowcount:
            return jsonify(error="Task not found."), 404
        return jsonify(ok=True)


@app.patch("/api/quick-log")
def quick_log():
    data = request.get_json(silent=True) or {}
    checks = {"sleep": lambda v: type(v) in (int,float) and 0 <= v <= 24, "energy": lambda v: type(v) is int and 1 <= v <= 5, "aptitude": lambda v: type(v) is int and 0 <= v <= 500, "aptitude_accuracy": lambda v: type(v) in (int,float) and 0 <= v <= 100, "coding_attempted": lambda v: type(v) is int and 0 <= v <= 500, "coding_solved": lambda v: type(v) is int and 0 <= v <= 500, "applications_submitted": lambda v: type(v) is int and 0 <= v <= 500, "linkedin_requests": lambda v: type(v) is int and 0 <= v <= 500, "speaking_minutes": lambda v: type(v) is int and 0 <= v <= 1440}
    text_fields = {"project_deliverable", "instagram_task", "blocker"}
    for key, value in data.items():
        if key in checks and not checks[key](value):
            return jsonify(error=f"Invalid {key} value."), 400
        if key in text_fields and (not isinstance(value, str) or len(value) > 1000):
            return jsonify(error=f"Invalid {key} value."), 400
        if key == "core_cs_done" and not isinstance(value, bool):
            return jsonify(error="Invalid core_cs_done value."), 400
        if key not in checks and key not in text_fields and key != "core_cs_done":
            return jsonify(error=f"Invalid {key} value."), 400
    with connect() as db:
        record = record_for(db)
        if data:
            db.execute("UPDATE daily_records SET " + ",".join(f"{key}=?" for key in data) + " WHERE id=?", (*data.values(), record["id"]))
        if "core_cs_done" in data:
            db.execute("UPDATE daily_records SET core_cs_done=? WHERE id=?", (int(data["core_cs_done"]), record["id"]))
        return jsonify(record=dict(db.execute("SELECT * FROM daily_records WHERE id=?", (record["id"],)).fetchone()))


@app.patch("/api/reflection")
def reflection():
    data = request.get_json(silent=True) or {}
    note = str(data.get("reflection", ""))[:2000]
    with connect() as db:
        record = record_for(db)
        db.execute("UPDATE daily_records SET reflection=?,light_day=? WHERE id=?", (note, int(bool(data.get("light_day", record["light_day"]))), record["id"]))
    return jsonify(ok=True)


@app.get("/api/stats")
def stats():
    with connect() as db:
        t = db.execute(
            "SELECT"
            " (SELECT COUNT(*) FROM entries WHERE kind='coding') c_coding,"
            " (SELECT COUNT(*) FROM entries WHERE kind='fundamentals') c_fund,"
            " (SELECT COUNT(*) FROM entries WHERE kind='jobs') c_jobs,"
            " (SELECT COUNT(*) FROM entries WHERE kind='projects') c_proj,"
            " (SELECT COUNT(*) FROM entries WHERE kind='questions') c_q,"
            " (SELECT COUNT(*) FROM entries WHERE kind='coding' AND status='Solved') solved,"
            " (SELECT COUNT(*) FROM entries WHERE kind='jobs' AND status IN ('Applied','Online Assessment','Interview','Offer','Rejected')) applied_records,"
            " (SELECT COALESCE(SUM(applications_submitted),0) FROM daily_records) applied_logs,"
            " (SELECT COUNT(*) FROM entries WHERE kind='fundamentals' AND status IN ('Completed','Solved','Done')) fundamentals_done,"
            " (SELECT COUNT(*) FROM entries WHERE kind='projects' AND status IN ('Completed','Done')) project_done,"
            " (SELECT COUNT(*) FROM entries WHERE kind='interview' AND status IN ('Attempted','Practiced','Solved','Completed')) interview_done,"
            " (SELECT COUNT(*) FROM (SELECT day_id FROM checklist WHERE done=1 GROUP BY day_id)) active_days,"
            " (SELECT COALESCE(SUM(coding_attempted),0) FROM daily_records) scorecard_attempts,"
            " (SELECT COALESCE(SUM(coding_solved),0) FROM daily_records) scorecard_solved,"
            " (SELECT value FROM settings WHERE key='streak_threshold') threshold,"
            " (SELECT COUNT(*) FROM checklist WHERE done=1) done_total"
        ).fetchone()
        counts = {"coding": t["c_coding"], "fundamentals": t["c_fund"], "jobs": t["c_jobs"], "projects": t["c_proj"], "questions": t["c_q"]}
        solved = t["solved"]
        applied = max(t["applied_records"], t["applied_logs"])
        fundamentals_done = t["fundamentals_done"]
        project_done = t["project_done"]
        interview_done = t["interview_done"]
        active_days = t["active_days"]
        scorecard_attempts = t["scorecard_attempts"]
        scorecard_solved = t["scorecard_solved"]
        readiness_parts = [("Coding", min(100, max(solved, scorecard_solved) * 5), 25), ("Fundamentals", min(100, fundamentals_done / 18 * 100), 20), ("Projects", min(100, project_done / 15 * 100), 20), ("Applications", min(100, applied / 10 * 100), 15), ("Interview practice", min(100, interview_done / 20 * 100), 10), ("Consistency", min(100, active_days / 20 * 100), 10)]
        has_activity = any((solved, scorecard_solved, fundamentals_done, project_done, applied, interview_done, active_days, scorecard_attempts))
        readiness_score = round(sum(score * weight for _, score, weight in readiness_parts) / 100) if has_activity else None
        done = db.execute("SELECT d.date,COUNT(*) completed FROM checklist c JOIN daily_records d ON d.id=c.day_id WHERE c.done=1 GROUP BY d.date ORDER BY d.date DESC").fetchall()
        threshold = int(t["threshold"])
        streak = 0
        expected = today()
        completed_by_day = {date.fromisoformat(r["date"]): r["completed"] for r in done}
        while completed_by_day.get(expected, 0) >= threshold:
            streak += 1
            expected -= timedelta(days=1)
        return jsonify(counts=counts, solved=solved, applied=applied, streak=streak, xp=solved*20+applied*15+t["done_total"]*5, threshold=threshold, readiness={"score":readiness_score,"breakdown":[{"name":name,"score":round(score)} for name,score,_ in readiness_parts],"interview_count":interview_done,"project_count":project_done})


@app.get("/api/settings")
def get_settings():
    with connect() as db:
        return jsonify({r["key"]: r["value"] for r in db.execute("SELECT key,value FROM settings")})


@app.patch("/api/settings")
def save_settings():
    data = request.get_json(silent=True) or {}
    allowed = {"theme", "plan_start", "streak_threshold"}
    if set(data)-allowed:
        return jsonify(error="Unsupported setting."), 400
    if "theme" in data and data["theme"] not in {"dark", "violet", "emerald", "light"}:
        return jsonify(error="Unknown theme."), 400
    if "streak_threshold" in data and (not str(data["streak_threshold"]).isdigit() or not 1 <= int(data["streak_threshold"]) <= 10):
        return jsonify(error="Streak threshold must be between 1 and 10."), 400
    if "plan_start" in data:
        try: date.fromisoformat(data["plan_start"])
        except (ValueError, TypeError): return jsonify(error="Use a valid ISO date."), 400
    with connect() as db:
        for key,value in data.items(): db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key,str(value)))
    if "plan_start" in data: initialize(force=True)
    return jsonify(ok=True)


@app.get("/api/backup")
def backup():
    with connect() as db:
        result = {table: [dict(row) for row in db.execute(f"SELECT * FROM {table}")] for table in ("settings", "daily_records", "checklist", "entries", "focus_sessions", "weekly_reviews", "curriculum", "resources", "legacy_records", "app_meta")}
        return jsonify(schema_version=3, data=result)


@app.post("/api/focus")
def log_focus():
    data = request.get_json(silent=True) or {}
    minutes = data.get("minutes")
    if not isinstance(minutes, int) or not 1 <= minutes <= 180: return jsonify(error="Minutes must be between 1 and 180."), 400
    with connect() as db: db.execute("INSERT INTO focus_sessions(started_at,minutes,subject) VALUES(?,?,?)", (datetime.now().isoformat(timespec="seconds"),minutes,str(data.get("subject", ""))[:120]))
    return jsonify(ok=True), 201


@app.get("/api/focus")
def focus_total():
    with connect() as db: return jsonify(minutes=db.execute("SELECT COALESCE(SUM(minutes),0) FROM focus_sessions WHERE date(started_at)=?", (today().isoformat(),)).fetchone()[0])


@app.get("/api/review")
def weekly_review():
    start = (today() - timedelta(days=today().weekday())).isoformat()
    end = today().isoformat()
    with connect() as db:
        r = db.execute(
            "SELECT"
            " (SELECT focus FROM weekly_reviews WHERE week_start=?) focus,"
            " (SELECT COALESCE(SUM(aptitude),0) FROM daily_records WHERE date BETWEEN ? AND ?) aptitude,"
            " (SELECT COALESCE(SUM(coding_attempted),0) FROM daily_records WHERE date BETWEEN ? AND ?) attempted,"
            " (SELECT COALESCE(SUM(coding_solved),0) FROM daily_records WHERE date BETWEEN ? AND ?) scorecard_solved,"
            " (SELECT COALESCE(SUM(applications_submitted),0) FROM daily_records WHERE date BETWEEN ? AND ?) applications,"
            " (SELECT COALESCE(SUM(linkedin_requests),0) FROM daily_records WHERE date BETWEEN ? AND ?) networking,"
            " (SELECT COALESCE(SUM(speaking_minutes),0) FROM daily_records WHERE date BETWEEN ? AND ?) speaking,"
            " (SELECT COUNT(*) FROM checklist c JOIN daily_records d ON d.id=c.day_id WHERE d.date BETWEEN ? AND ? AND c.done=1) checklist_done,"
            " (SELECT COUNT(*) FROM entries WHERE kind='coding' AND status='Solved' AND date(updated_at) BETWEEN ? AND ?) solved,"
            " (SELECT COUNT(*) FROM entries WHERE kind='jobs' AND status NOT IN ('To Apply','Not Started') AND date(updated_at) BETWEEN ? AND ?) job_apps",
            (start, *(start, end) * 9),
        ).fetchone()
        scorecard = {k: r[k] for k in ("aptitude", "attempted", "scorecard_solved", "applications", "networking", "speaking")}
        return jsonify(week_start=start, focus=r["focus"] or "", checklist_done=r["checklist_done"], solved=r["solved"], applications=r["job_apps"], scorecard=scorecard)


@app.put("/api/review")
def save_review():
    data=request.get_json(silent=True) or {}; focus=str(data.get("focus", ""))[:1000]; start=(today()-timedelta(days=today().weekday())).isoformat()
    with connect() as db: db.execute("INSERT INTO weekly_reviews(week_start,focus,created_at) VALUES(?,?,?) ON CONFLICT(week_start) DO UPDATE SET focus=excluded.focus",(start,focus,datetime.now().isoformat(timespec="seconds")))
    return jsonify(ok=True)


@app.cli.command("init-db")
def init_db_command():
    initialize()
    print(f"Database ready: {DB_PATH}")


initialize()

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    import socket
    import threading
    import webbrowser
    port = 5000
    while True:
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) != 0: break
        port += 1
    address = f"http://127.0.0.1:{port}"
    print(f"Placement Command Centre: {address}")
    threading.Timer(1, webbrowser.open, args=(address,)).start()
    run_simple("127.0.0.1", port, app, use_reloader=False)