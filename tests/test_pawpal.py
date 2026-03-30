"""
tests/test_pawpal.py
PawPal+ — automated test suite
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


# ---------------------------------------------------------------------------
# Fixtures — reusable setup
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_owner():
    """Owner with two pets and several tasks."""
    owner = Owner(name="Alex", available_minutes=90)
    buddy = Pet(name="Buddy", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    buddy.add_task(Task(name="Morning walk",   duration_minutes=30, priority=5, category="walk",    recurrence="daily",  start_time="08:00"))
    buddy.add_task(Task(name="Breakfast",      duration_minutes=10, priority=5, category="feeding", recurrence="daily",  start_time="08:20"))
    buddy.add_task(Task(name="Flea treatment", duration_minutes=15, priority=3, category="meds",    recurrence="weekly", start_time="09:00"))
    luna.add_task(Task(name="Feeding",         duration_minutes=10, priority=5, category="feeding", recurrence="daily",  start_time="08:00"))
    luna.add_task(Task(name="Litter box",      duration_minutes=5,  priority=4, category="grooming",recurrence="daily",  start_time="08:15"))
    owner.add_pet(buddy)
    owner.add_pet(luna)
    return owner


# ---------------------------------------------------------------------------
# Task — basic behaviour
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should set completed to True."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_reset_clears_completion():
    """reset() should set completed back to False."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    task.mark_complete()
    task.reset()
    assert task.completed is False


def test_is_feasible_true_when_fits():
    """is_feasible() returns True when duration fits the budget."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.is_feasible(30) is True
    assert task.is_feasible(60) is True


def test_is_feasible_false_when_too_long():
    """is_feasible() returns False when duration exceeds the budget."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.is_feasible(20) is False


def test_end_time_calculated_correctly():
    """end_time() should return start_time + duration as HH:MM."""
    task = Task(name="Walk", duration_minutes=30, priority=3, start_time="08:00")
    assert task.end_time() == "08:30"


def test_end_time_none_when_no_start():
    """end_time() should return None if no start_time is set."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.end_time() is None


# ---------------------------------------------------------------------------
# Task — recurrence
# ---------------------------------------------------------------------------

def test_next_occurrence_daily():
    """Daily task should create a next occurrence for tomorrow."""
    today = date.today().isoformat()
    task = Task(name="Walk", duration_minutes=30, priority=5, recurrence="daily", due_date=today)
    next_task = task.next_occurrence()
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert next_task is not None
    assert next_task.due_date == expected


def test_next_occurrence_weekly():
    """Weekly task should create a next occurrence 7 days out."""
    today = date.today().isoformat()
    task = Task(name="Bath", duration_minutes=20, priority=3, recurrence="weekly", due_date=today)
    next_task = task.next_occurrence()
    expected = (date.today() + timedelta(days=7)).isoformat()
    assert next_task is not None
    assert next_task.due_date == expected


def test_next_occurrence_none_for_nonrecurring():
    """Non-recurring task should return None from next_occurrence()."""
    task = Task(name="Vet visit", duration_minutes=60, priority=4, recurrence="none")
    assert task.next_occurrence() is None


def test_next_occurrence_preserves_attributes():
    """Next occurrence should inherit name, duration, priority, and category."""
    task = Task(name="Walk", duration_minutes=30, priority=5, category="walk", recurrence="daily")
    next_task = task.next_occurrence()
    assert next_task.name == task.name
    assert next_task.duration_minutes == task.duration_minutes
    assert next_task.priority == task.priority
    assert next_task.category == task.category


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task should increase the pet's task count by 1."""
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Walk", duration_minutes=30, priority=3))
    assert len(pet.get_tasks()) == 1


def test_add_task_sets_pet_name():
    """add_task() should set the task's pet_name to the pet's name."""
    pet = Pet(name="Luna", species="cat")
    task = Task(name="Feeding", duration_minutes=10, priority=5)
    pet.add_task(task)
    assert task.pet_name == "Luna"


def test_remove_task_decreases_count():
    """remove_task() should decrease the pet's task count."""
    pet = Pet(name="Buddy", species="dog")
    task = Task(name="Walk", duration_minutes=30, priority=3)
    pet.add_task(task)
    pet.remove_task(task.task_id)
    assert len(pet.get_tasks()) == 0


def test_pet_with_no_tasks_returns_empty_list():
    """get_tasks() on a pet with no tasks should return an empty list."""
    pet = Pet(name="Buddy", species="dog")
    assert pet.get_tasks() == []


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

def test_add_pet_increases_count():
    """add_pet() should increase the owner's pet count."""
    owner = Owner(name="Alex", available_minutes=60)
    assert len(owner.get_pets()) == 0
    owner.add_pet(Pet(name="Buddy", species="dog"))
    assert len(owner.get_pets()) == 1


def test_get_all_tasks_spans_all_pets():
    """get_all_tasks() should return tasks from every pet combined."""
    owner = Owner(name="Alex", available_minutes=60)
    buddy = Pet(name="Buddy", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    buddy.add_task(Task(name="Walk",    duration_minutes=30, priority=3))
    luna.add_task(Task(name="Feeding",  duration_minutes=10, priority=5))
    luna.add_task(Task(name="Brushing", duration_minutes=15, priority=2))
    owner.add_pet(buddy)
    owner.add_pet(luna)
    assert len(owner.get_all_tasks()) == 3


def test_owner_with_no_pets_returns_empty_task_list():
    """get_all_tasks() on an owner with no pets should return empty list."""
    owner = Owner(name="Alex", available_minutes=60)
    assert owner.get_all_tasks() == []


# ---------------------------------------------------------------------------
# Scheduler — core scheduling
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_budget(sample_owner):
    """Total scheduled duration must not exceed available_minutes."""
    plan = Scheduler(sample_owner).generate_plan()
    total = sum(t.duration_minutes for t in plan.tasks)
    assert total <= sample_owner.available_minutes


def test_scheduler_prioritises_high_priority_tasks():
    """Higher priority tasks should appear before lower priority ones."""
    owner = Owner(name="Alex", available_minutes=30)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(name="Low",  duration_minutes=20, priority=1))
    pet.add_task(Task(name="High", duration_minutes=20, priority=5))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert plan.tasks[0].name == "High"


def test_scheduler_skips_completed_tasks():
    """Already-completed tasks should not appear in the plan."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    task = Task(name="Walk", duration_minutes=30, priority=5)
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert task not in plan.tasks


def test_validate_constraints_catches_zero_time():
    """validate_constraints() should warn when available_minutes is 0."""
    owner = Owner(name="Alex", available_minutes=0)
    owner.add_pet(Pet(name="Buddy", species="dog"))
    warnings = Scheduler(owner).validate_constraints()
    assert any("0 minutes" in w for w in warnings)


def test_validate_constraints_catches_no_pets():
    """validate_constraints() should warn when owner has no pets."""
    owner = Owner(name="Alex", available_minutes=60)
    warnings = Scheduler(owner).validate_constraints()
    assert any("No pets" in w for w in warnings)


# ---------------------------------------------------------------------------
# Scheduler — sorting
# ---------------------------------------------------------------------------

def test_sort_by_duration_ascending(sample_owner):
    """sort_tasks_by_duration() should return tasks shortest-first."""
    sorted_tasks = Scheduler(sample_owner).sort_tasks_by_duration()
    durations = [t.duration_minutes for t in sorted_tasks]
    assert durations == sorted(durations)


def test_sort_by_start_time_chronological(sample_owner):
    """sort_tasks_by_start_time() should return timed tasks in HH:MM order."""
    scheduler = Scheduler(sample_owner)
    sorted_tasks = scheduler.sort_tasks_by_start_time()
    timed = [t for t in sorted_tasks if t.start_time]
    times = [t.start_time for t in timed]
    assert times == sorted(times)


def test_sort_tasks_without_start_time_go_last(sample_owner):
    """Tasks with no start_time should appear at the end after sorting."""
    pet = sample_owner.get_pets()[0]
    pet.add_task(Task(name="No-time task", duration_minutes=10, priority=2))
    sorted_tasks = Scheduler(sample_owner).sort_tasks_by_start_time()
    last = sorted_tasks[-1]
    assert last.start_time == ""


# ---------------------------------------------------------------------------
# Scheduler — filtering
# ---------------------------------------------------------------------------

def test_filter_by_pet_name(sample_owner):
    """filter_tasks(pet_name=) should return only that pet's tasks."""
    tasks = Scheduler(sample_owner).filter_tasks(pet_name="Buddy")
    assert all(t.pet_name == "Buddy" for t in tasks)


def test_filter_by_completed_status(sample_owner):
    """filter_tasks(completed=False) should return only incomplete tasks."""
    tasks = Scheduler(sample_owner).filter_tasks(completed=False)
    assert all(not t.completed for t in tasks)


def test_filter_by_category(sample_owner):
    """filter_tasks(category=) should return only tasks of that category."""
    tasks = Scheduler(sample_owner).filter_tasks(category="feeding")
    assert all(t.category == "feeding" for t in tasks)
    assert len(tasks) == 2  # Buddy breakfast + Luna feeding


# ---------------------------------------------------------------------------
# Scheduler — conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_pet_overlap():
    """Two overlapping tasks for the same pet should produce a conflict warning."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(name="Walk",      duration_minutes=30, priority=5, start_time="08:00"))
    pet.add_task(Task(name="Breakfast", duration_minutes=10, priority=4, start_time="08:20"))
    owner.add_pet(pet)
    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) > 0
    assert "Buddy" in conflicts[0]


def test_detect_conflicts_exact_same_time():
    """Two tasks at the exact same time for the same pet should conflict."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(name="Task A", duration_minutes=20, priority=5, start_time="09:00"))
    pet.add_task(Task(name="Task B", duration_minutes=15, priority=3, start_time="09:00"))
    owner.add_pet(pet)
    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) > 0


def test_no_conflict_when_tasks_sequential():
    """Tasks that run back-to-back (not overlapping) should not conflict."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(name="Walk",      duration_minutes=30, priority=5, start_time="08:00"))
    pet.add_task(Task(name="Breakfast", duration_minutes=10, priority=4, start_time="08:30"))
    owner.add_pet(pet)
    conflicts = Scheduler(owner).detect_conflicts()
    assert conflicts == []


def test_no_conflict_different_pets_same_time():
    """Same time tasks for different pets should not conflict."""
    owner = Owner(name="Alex", available_minutes=60)
    buddy = Pet(name="Buddy", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    buddy.add_task(Task(name="Walk",    duration_minutes=30, priority=5, start_time="08:00"))
    luna.add_task(Task(name="Feeding",  duration_minutes=10, priority=5, start_time="08:00"))
    owner.add_pet(buddy)
    owner.add_pet(luna)
    conflicts = Scheduler(owner).detect_conflicts()
    assert conflicts == []


# ---------------------------------------------------------------------------
# Scheduler — recurring task reset
# ---------------------------------------------------------------------------

def test_reset_recurring_creates_new_task():
    """Completing a daily task should add a new task due tomorrow."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    task = Task(name="Walk", duration_minutes=30, priority=5, recurrence="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    task.mark_complete()
    new_tasks = Scheduler(owner).reset_recurring_tasks()
    assert len(new_tasks) == 1
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert new_tasks[0].due_date == expected


def test_reset_recurring_does_not_affect_nonrecurring():
    """Completing a non-recurring task should not create a new task."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    task = Task(name="Vet visit", duration_minutes=60, priority=4, recurrence="none")
    pet.add_task(task)
    owner.add_pet(pet)
    task.mark_complete()
    new_tasks = Scheduler(owner).reset_recurring_tasks()
    assert new_tasks == []