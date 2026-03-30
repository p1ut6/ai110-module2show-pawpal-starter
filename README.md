# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

Phase 3 added the following algorithmic features to `pawpal_system.py`:

- **Sorting** — tasks can be sorted by duration (shortest first) or by start time using `sorted()` with a lambda key
- **Filtering** — `Scheduler.filter_tasks()` filters the full task list by pet name, completion status, or category
- **Recurring tasks** — tasks with `recurrence="daily"` or `recurrence="weekly"` automatically generate a next occurrence using Python's `timedelta` when marked complete
- **Conflict detection** — `Scheduler.detect_conflicts()` checks for overlapping time windows among tasks with a `start_time` set, using the interval overlap condition `start_A < end_B and start_B < end_A`

These features are verified in `main.py` and surfaced in the Streamlit UI via the start time input field and conflict warning display on the Today's Plan tab.
