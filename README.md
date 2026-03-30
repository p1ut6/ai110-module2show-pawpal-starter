# PawPal+ 🐾

A Streamlit app that helps a busy pet owner build a smart daily care plan for their pets — automatically prioritized, conflict-checked, and clearly explained.

---


## ✨ Features

- **Priority-based scheduling** — the `Scheduler` engine sorts tasks by priority (1–5) and greedily fills the owner's available time budget, ensuring must-do tasks are always scheduled first.
- **Sorting** — tasks can be sorted by duration (shortest first) or by start time using `sorted()` with a lambda key, surfaced as dropdown controls on the Tasks tab.
- **Filtering** — `Scheduler.filter_tasks()` filters the full task list by pet name, completion status, or category, letting owners zero in on exactly what they need.
- **Conflict detection** — `Scheduler.detect_conflicts()` checks for overlapping time windows among timed tasks for the same pet, using the interval overlap condition `start_A < end_B and start_B < end_A`. Conflicts are surfaced prominently in the UI as red error banners.
- **Daily and weekly recurrence** — tasks marked with `recurrence="daily"` or `recurrence="weekly"` automatically generate a next occurrence using Python's `timedelta` when marked complete, so routine care tasks never fall through the cracks.
- **Plain-English reasoning** — every generated plan includes a human-readable explanation of which tasks were scheduled, which were skipped, and why.
- **Input validation** — `Scheduler.validate_constraints()` catches problems (no pets, zero time, invalid priority) before scheduling runs, surfacing warnings directly in the UI.

---

## 🗂 Project structure

```
pawpal_plus/
├── app.py               # Streamlit UI
├── pawpal_system.py     # Logic layer: Task, Pet, Owner, Scheduler, DailyPlan
├── main.py              # Demo / smoke-test script
├── tests/
│   └── test_pawpal.py   # 34-test pytest suite
├── uml_final.png        # Final class diagram
├── README.md
├── reflection.md
└── requirements.txt
```

---

## ⚙️ Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧪 Running tests

```bash
python -m pytest tests/ -v
```

The suite covers 34 tests across: Task completion and recurrence, Pet and Owner task management, Scheduler core logic, sorting, filtering, conflict detection, and recurring task reset.

**Confidence level: ⭐⭐⭐⭐ (4/5)** — core logic and edge cases are well covered; integration tests (full UI → plan flow) are the main remaining gap.

---

## 🏗 Architecture

See `uml_final.png` for the full class diagram. The key design principle is **separation of concerns**: all scheduling logic lives in `pawpal_system.py` as plain Python classes; `app.py` stays thin and only calls methods — it contains no scheduling logic of its own.

| Class | Responsibility |
|---|---|
| `Task` | Single care item with duration, priority, recurrence, and time window |
| `Pet` | Owns a list of tasks; sets `pet_name` on each task when added |
| `Owner` | Holds pets and time budget; aggregates all tasks across pets |
| `Scheduler` | Core engine: schedule, sort, filter, conflict-detect, validate |
| `DailyPlan` | Output object: scheduled tasks, skipped tasks, conflicts, reasoning |