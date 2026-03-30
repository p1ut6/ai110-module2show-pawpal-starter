"""
pawpal_system.py
PawPal+ — logic layer (skeleton)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int                         # 1 (low) – 5 (high)
    category: str = "general"            # walk | feeding | meds | grooming | enrichment | other
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    completed: bool = False

    # --- behaviour ---

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        raise NotImplementedError

    def reset(self) -> None:
        """Reset completion status (e.g. for a new day)."""
        raise NotImplementedError

    def is_feasible(self, available_minutes: int) -> bool:
        """Return True if the task fits within the available time budget."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    _tasks: list[Task] = field(default_factory=list, repr=False)

    # --- behaviour ---

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its ID."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_minutes: int                # total free time today
    preferences: dict = field(default_factory=dict)   # e.g. {"prefer_morning": True}
    _pets: list[Pet] = field(default_factory=list, repr=False)

    # --- behaviour ---

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        """Return all registered pets."""
        raise NotImplementedError

    def update_preferences(self, prefs: dict) -> None:
        """Merge new preferences into the existing preferences dict."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    tasks: list[Task]
    skipped: list[Task]
    reasoning: str
    date: str = field(default_factory=lambda: date.today().isoformat())

    # --- behaviour ---

    def to_dict(self) -> dict:
        """Serialise the plan to a plain dict (useful for display / storage)."""
        raise NotImplementedError

    def summary(self) -> str:
        """Return a short human-readable summary of the plan."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Core scheduling engine.

    Scheduling strategy (to implement):
      1. Filter tasks that are feasible given available_minutes.
      2. Sort remaining tasks by priority (desc), then duration (asc) as tiebreaker.
      3. Greedily select tasks until the time budget is exhausted.
      4. Record skipped tasks and build a reasoning string.
    """

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.schedule: list[Task] = []

    # --- behaviour ---

    def generate_plan(self) -> DailyPlan:
        """
        Build and return a DailyPlan for today.

        Constraints to respect:
          - Total scheduled duration <= owner.available_minutes
          - Tasks with higher priority are selected first
          - Tasks that don't fit are added to the skipped list
        """
        raise NotImplementedError

    def explain_plan(self, plan: DailyPlan) -> str:
        """
        Return a plain-English explanation of why tasks were chosen / skipped.

        Example: "Feeding was prioritised (priority 5). Walk was skipped because
                  only 10 minutes remained and it needs 30 minutes."
        """
        raise NotImplementedError

    def get_skipped_tasks(self, plan: DailyPlan) -> list[Task]:
        """Return the list of tasks that could not be scheduled."""
        raise NotImplementedError

    def total_duration(self, tasks: Optional[list[Task]] = None) -> int:
        """Sum the durations of the given tasks (defaults to current schedule)."""
        raise NotImplementedError

    def validate_constraints(self) -> list[str]:
        """
        Check for obvious problems before scheduling.

        Returns a list of warning strings (empty list = all clear).
        Examples:
          - "No tasks defined for <pet name>"
          - "Available time is 0 minutes"
          - "Task '<name>' has an invalid priority (must be 1–5)"
        """
        raise NotImplementedError