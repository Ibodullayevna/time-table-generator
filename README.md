# Automated University Timetable Generator
Web app + CSP solver (Python, Flask, Google OR-Tools CP-SAT). Enter the university structure, professors, subjects and
time matrix in the browser -> get conflict-free timetables for **every student group** and **every professor**
(print / save as PDF from the browser).

## Run
    pip install -r requirements.txt
    python app.py            # open http://localhost:5000
    python scheduler.py sample_input.json   # CLI, text output

## Files
- `scheduler.py`  - CSP model + hard constraints (H1-H6, documented in the header) + result builder
- `app.py`        - Flask API (`/api/generate`, `/api/sample`)
- `static/index.html` - input wizard + timetable grid renderer
- `sample_input.json` - JSON data model (example = 4th Year AIML timetable)
- `schema.sql`    - PostgreSQL schema; UNIQUE keys enforce no group/teacher overlap

## Input notes
- Credits = weekly hours (override with `"hours"` per subject in JSON).
- `reserved` = slot numbers never scheduled for that year (shown as the empty-slot label, e.g. "Project Work").
- Breaks >= 30 min (lunch) separate slots: same subject may sit before and after it; short breaks do not.
- If no solution exists, the app tells you why (capacity, professor load, availability).
