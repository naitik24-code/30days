# Daylight — Placement Command Centre

A local-first daily placement preparation tool. It runs on `127.0.0.1`, stores tracker data in SQLite, and makes no network requests from the page.

## Start

On Windows, double-click `run.bat`. The script creates `.venv`, installs the packages in `requirements.txt` when that file changes, starts the local server, and opens the browser. To run it manually, use Python 3.10+ with Flask installed:

```powershell
python app.py
```

The default address is `http://127.0.0.1:5000`. If the port is busy, the server checks the next available port and prints its address in the terminal.

## Data and backups

The SQLite database is `data/placement.db` beside `app.py` (or the path in `PLACEMENT_DB`). SQLite foreign keys and WAL mode are enabled for each connection. A new run creates the database and today's checklist without replacing existing records. Mutating API requests require a session CSRF token. JSON backup downloads are available in Settings.

The supplied files are copied into `data/source_pack/` and imported once on first launch. That imports 30 roadmap days, 15 schedule blocks, 11 unchecked Day 1 setup steps, 18 fundamentals, 126 practice questions, 52 interview questions, and 15 project tasks. The 87 rows in the original tracker backup stay in a separate archive; its 43 historical `Done` statuses do not count as current progress. The job and spaced-revision CSVs are empty, so those screens stay empty. Blank scorecard/review files are treated as templates, never as logged activity.

The database is local to this computer. Keep a copy of the downloaded JSON backup somewhere safe. The current version supports exporting a backup; in-app restore and automatic rotating backups are not implemented yet.

## Use

- **Today:** work from the imported day-by-day roadmap, follow the local-time timetable, finish the Day 1 setup checklist, log scorecard signals, reflect, and run a focus timer. The 30-day trail uses saved checklist rows.
- **Practice:** review the 126 supplied practice prompts, 18 fundamentals, and 52 interview questions. Their source statuses remain `Not Started` until you change them.
- **Career:** work through the 15 supplied project audit tasks and add genuine job applications as they happen.
- **Progress:** view actual saved totals, a checklist completion chart, weighted readiness breakdown, streak/XP, and weekly scorecard totals.
- **Library:** read the supplied learning guide, cheat sheet, dashboard guide, Notion setup notes, mastery rule, and original tracker archive.
- **Settings:** pick a theme, plan start, and streak threshold; download a JSON backup.

## Assumptions and limitations

- The local machine's date is the plan's local date; one helper supplies the date used by server calculations.
- Checklist templates use ten stable defaults. Custom checklist templates, full schedule editing, question flashcards, CSV import/export, backup restore, automatic rotating backups, and browser reminders are not implemented yet.
- Tracker records share a compact generic schema; only fields meaningful to the current screen are exposed.
- Streaks count consecutive calendar days at or above the configured checklist threshold. XP is calculated from completed checklist tasks, solved coding entries, and active job applications.
- Readiness is weighted from saved coding, fundamentals, projects, applications, interview practice, and consistency data. It remains blank until there is actual activity. Some achievement types still need event tracking and remain locked.
- Fonts use installed system fallbacks so the app remains fully offline; fonts are not bundled in this workspace.
- Browser reminders and finish-day streak locking are not implemented. The site never invents activity or sample records.

## Tests

Install the development dependencies and run:

```powershell
python -m pytest
```

Tests use an isolated temporary SQLite database.
