"""
tests/test_pawpal.py
PawPal+ — unit tests
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_reset_clears_completion():
    """Calling reset() after mark_complete() should set completed back to False."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    task.mark_complete()
    task.reset()
    assert task.completed is False


def test_is_feasible_true_when_fits():
    """is_feasible() returns True when task duration fits the budget."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.is_feasible(30) is True
    assert task.is_feasible(60) is True


def test_is_feasible_false_when_too_long():
    """is_feasible() returns False when task duration exceeds the budget."""
    task = Task(name="Walk", duration_minutes=30, priority=3)
    assert task.is_feasible(20) is False


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task to a pet should increase its task count by 1."""
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Walk", duration_minutes=30, priority=3))
    assert len(pet.get_tasks()) == 1


def test_add_task_sets_pet_name():
    """add_task() should automatically set the task's pet_name field."""
    pet = Pet(name="Luna", species="cat")
    task = Task(name="Feeding", duration_minutes=10, priority=5)
    pet.add_task(task)
    assert task.pet_name == "Luna"


def test_remove_task_decreases_count():
    """Removing a task by ID should decrease the pet's task count."""
    pet = Pet(name="Buddy", species="dog")
    task = Task(name="Walk", duration_minutes=30, priority=3)
    pet.add_task(task)
    pet.remove_task(task.task_id)
    assert len(pet.get_tasks()) == 0


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

def test_add_pet_increases_count():
    """Adding a pet to an owner should increase the pet count."""
    owner = Owner(name="Alex", available_minutes=60)
    assert len(owner.get_pets()) == 0
    owner.add_pet(Pet(name="Buddy", species="dog"))
    assert len(owner.get_pets()) == 1


def test_get_all_tasks_returns_tasks_across_pets():
    """get_all_tasks() should return tasks from all pets combined."""
    owner = Owner(name="Alex", available_minutes=60)
    buddy = Pet(name="Buddy", species="dog")
    luna = Pet(name="Luna", species="cat")
    buddy.add_task(Task(name="Walk",    duration_minutes=30, priority=3))
    luna.add_task(Task(name="Feeding",  duration_minutes=10, priority=5))
    luna.add_task(Task(name="Brushing", duration_minutes=15, priority=2))
    owner.add_pet(buddy)
    owner.add_pet(luna)
    assert len(owner.get_all_tasks()) == 3


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_budget():
    """Scheduler should not schedule tasks that exceed available_minutes."""
    owner = Owner(name="Alex", available_minutes=20)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(name="Walk",    duration_minutes=30, priority=5))
    pet.add_task(Task(name="Feeding", duration_minutes=10, priority=4))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    total = sum(t.duration_minutes for t in plan.tasks)
    assert total <= 20


def test_scheduler_prioritises_high_priority_tasks():
    """Higher priority tasks should be scheduled before lower priority ones."""
    owner = Owner(name="Alex", available_minutes=30)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(name="Low priority",  duration_minutes=20, priority=1))
    pet.add_task(Task(name="High priority", duration_minutes=20, priority=5))
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()
    assert plan.tasks[0].name == "High priority"


def test_scheduler_skips_completed_tasks():
    """Tasks already marked complete should not appear in the plan."""
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