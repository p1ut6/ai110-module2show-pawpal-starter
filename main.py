"""
main.py
PawPal+ — demo script (Phase 3 update)
"""

from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

owner = Owner(name="Alex", available_minutes=90)

buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
buddy.add_task(Task(name="Morning walk",   duration_minutes=30, priority=5, category="walk",      recurrence="daily",  start_time="08:00"))
buddy.add_task(Task(name="Breakfast",      duration_minutes=10, priority=5, category="feeding",   recurrence="daily",  start_time="08:20"))
buddy.add_task(Task(name="Flea treatment", duration_minutes=15, priority=3, category="meds",      recurrence="weekly", start_time="09:00"))
buddy.add_task(Task(name="Fetch session",  duration_minutes=20, priority=2, category="enrichment",                     start_time="09:00"))  # conflict with flea treatment!

luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)
luna.add_task(Task(name="Feeding",         duration_minutes=10, priority=5, category="feeding",   recurrence="daily",  start_time="08:00"))
luna.add_task(Task(name="Litter box",      duration_minutes=5,  priority=4, category="grooming",  recurrence="daily",  start_time="08:15"))
luna.add_task(Task(name="Brushing",        duration_minutes=15, priority=2, category="grooming",  recurrence="weekly"))

owner.add_pet(buddy)
owner.add_pet(luna)

scheduler = Scheduler(owner)

# ---------------------------------------------------------------------------
# 1. Generate plan (includes conflict detection)
# ---------------------------------------------------------------------------

print("=" * 55)
print("        🐾  PawPal+ — Today's Schedule")
print("=" * 55)
plan = scheduler.generate_plan()
print(plan.summary())

# ---------------------------------------------------------------------------
# 2. Sorting demo
# ---------------------------------------------------------------------------

print("\n--- Sorted by duration (shortest first) ---")
for t in scheduler.sort_tasks_by_duration():
    print(f"  {t.duration_minutes:3} min — {t.name} ({t.pet_name})")

print("\n--- Sorted by start time ---")
for t in scheduler.sort_tasks_by_start_time():
    time_str = t.start_time if t.start_time else "no time"
    print(f"  {time_str} — {t.name} ({t.pet_name})")

# ---------------------------------------------------------------------------
# 3. Filtering demo
# ---------------------------------------------------------------------------

print("\n--- Filter: Buddy's tasks only ---")
for t in scheduler.filter_tasks(pet_name="Buddy"):
    print(f"  {t.name} — priority {t.priority}")

print("\n--- Filter: incomplete tasks ---")
for t in scheduler.filter_tasks(completed=False):
    print(f"  {t.name} ({t.pet_name})")

# ---------------------------------------------------------------------------
# 4. Recurring tasks demo
# ---------------------------------------------------------------------------

print("\n--- Recurring task reset demo ---")
# Mark Buddy's morning walk complete
buddy_tasks = buddy.get_tasks()
walk = next(t for t in buddy_tasks if t.name == "Morning walk")
walk.mark_complete()
print(f"  Marked '{walk.name}' complete (due: {walk.due_date})")

new_tasks = scheduler.reset_recurring_tasks()
for t in new_tasks:
    print(f"  Next occurrence created: '{t.name}' due {t.due_date}")

# ---------------------------------------------------------------------------
# 5. Conflict detection demo
# ---------------------------------------------------------------------------

print("\n--- Conflict detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(f"  ⚠  {c}")
else:
    print("  No conflicts detected.")

print("=" * 55)