"""
main.py
PawPal+ — demo script / testing ground
"""

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

owner = Owner(name="Alex", available_minutes=90)

# Pet 1
buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
buddy.add_task(Task(name="Morning walk",   duration_minutes=30, priority=5, category="walk",     recurrence="daily"))
buddy.add_task(Task(name="Breakfast",      duration_minutes=10, priority=5, category="feeding",  recurrence="daily"))
buddy.add_task(Task(name="Flea treatment", duration_minutes=15, priority=3, category="meds",     recurrence="weekly"))
buddy.add_task(Task(name="Fetch session",  duration_minutes=20, priority=2, category="enrichment"))

# Pet 2
luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)
luna.add_task(Task(name="Feeding",         duration_minutes=10, priority=5, category="feeding",  recurrence="daily"))
luna.add_task(Task(name="Litter box",      duration_minutes=5,  priority=4, category="grooming", recurrence="daily"))
luna.add_task(Task(name="Brushing",        duration_minutes=15, priority=2, category="grooming", recurrence="weekly"))

owner.add_pet(buddy)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Validate + schedule
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner)

warnings = scheduler.validate_constraints()
if warnings:
    print("⚠  Warnings:")
    for w in warnings:
        print(f"   {w}")
    print()

plan = scheduler.generate_plan()

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

print("=" * 50)
print("       🐾  PawPal+ — Today's Schedule")
print("=" * 50)
print(plan.summary())
print()
print("📋  Reasoning:")
print(f"   {scheduler.explain_plan(plan)}")
print("=" * 50)