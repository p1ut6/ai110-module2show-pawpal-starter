"""
pawpal_system.py
PawPal+ — logic layer
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int                          # 1 (low) – 5 (high)
    category: str = "general"             # walk | feeding | meds | grooming | enrichment | other
    recurrence: str = "none"              # "none" | "daily" | "weekly"
    pet_name: str = ""                    # which pet this task belongs to
    start_time: str = ""                  # optional "HH:MM" e.g. "09:00"
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    completed: bool = False
    due_date: str = field(default_factory=lambda: date.today().isoformat())

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        self.completed = True

    def reset(self) -> None:
        """Reset completion status (e.g. for a new day)."""
        self.completed = False

    def is_feasible(self, available_minutes: int) -> bool:
        """Return True if the task fits within the available time budget."""
        return self.duration_minutes <= available_minutes

    def next_occurrence(self) -> Optional[Task]:
        """
        Return a fresh copy of this task due on its next recurrence date,
        or None if the task is non-recurring.
        Uses timedelta to calculate today + 1 day (daily) or + 7 days (weekly).
        """
        if self.recurrence == "none":
            return None
        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(days=7)
        next_date = (datetime.fromisoformat(self.due_date) + delta).date().isoformat()
        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            recurrence=self.recurrence,
            pet_name=self.pet_name,
            start_time=self.start_time,
            due_date=next_date,
        )

    def end_time(self) -> Optional[str]:
        """
        Return the calculated end time as "HH:MM" based on start_time + duration,
        or None if no start_time is set.
        """
        if not self.start_time:
            return None
        start = datetime.strptime(self.start_time, "%H:%M")
        end = start + timedelta(minutes=self.duration_minutes)
        return end.strftime("%H:%M")


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

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        task.pet_name = self.name
        self._tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its ID."""
        self._tasks = [t for t in self._tasks if t.task_id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self._tasks)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_minutes: int                 # total free time today
    preferences: dict = field(default_factory=dict)
    _pets: list[Pet] = field(default_factory=list, repr=False)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self._pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all registered pets."""
        return list(self._pets)

    def update_preferences(self, prefs: dict) -> None:
        """Merge new preferences into the existing preferences dict."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets (used by Scheduler)."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks())
        return tasks


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    tasks: list[Task]
    skipped: list[Task]
    reasoning: str
    conflicts: list[str] = field(default_factory=list)
    date: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> dict:
        """Serialise the plan to a plain dict."""
        return {
            "date": self.date,
            "tasks": [
                {
                    "task_id": t.task_id,
                    "name": t.name,
                    "pet": t.pet_name,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "category": t.category,
                    "recurrence": t.recurrence,
                    "start_time": t.start_time,
                    "end_time": t.end_time(),
                    "completed": t.completed,
                }
                for t in self.tasks
            ],
            "skipped": [
                {
                    "task_id": t.task_id,
                    "name": t.name,
                    "pet": t.pet_name,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                }
                for t in self.skipped
            ],
            "conflicts": self.conflicts,
            "reasoning": self.reasoning,
        }

    def summary(self) -> str:
        """Return a short human-readable summary of the plan."""
        total = sum(t.duration_minutes for t in self.tasks)
        lines = [f"Daily plan for {self.date}"]
        lines.append(f"  Scheduled: {len(self.tasks)} task(s) — {total} min total")
        for t in self.tasks:
            time_str = f" @ {t.start_time}–{t.end_time()}" if t.start_time else ""
            lines.append(f"    [{t.priority}★] {t.name} ({t.pet_name}) — {t.duration_minutes} min{time_str}")
        if self.skipped:
            lines.append(f"  Skipped: {len(self.skipped)} task(s)")
            for t in self.skipped:
                lines.append(f"    {t.name} ({t.pet_name}) — needed {t.duration_minutes} min")
        if self.conflicts:
            lines.append(f"  Conflicts ({len(self.conflicts)}):")
            for c in self.conflicts:
                lines.append(f"    ⚠ {c}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Core scheduling engine.

    Strategy:
      1. Collect all tasks from all of the owner's pets.
      2. Validate inputs and surface any warnings.
      3. Filter out already-completed tasks.
      4. Sort by priority (desc), then duration (asc) as tiebreaker.
      5. Greedily select tasks until the time budget is exhausted.
      6. Detect time conflicts among scheduled tasks.
      7. Record skipped tasks and build a plain-English reasoning string.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    # --- core ---

    def generate_plan(self) -> DailyPlan:
        """Build and return a DailyPlan for today."""
        all_tasks = self.owner.get_all_tasks()
        candidates = [t for t in all_tasks if not t.completed]
        candidates.sort(key=lambda t: (-t.priority, t.duration_minutes))

        scheduled = []
        skipped = []
        budget = self.owner.available_minutes

        for task in candidates:
            if task.is_feasible(budget):
                scheduled.append(task)
                budget -= task.duration_minutes
            else:
                skipped.append(task)

        conflicts = self.detect_conflicts(scheduled)
        reasoning = self._build_reasoning(scheduled, skipped, self.owner.available_minutes)
        return DailyPlan(tasks=scheduled, skipped=skipped, reasoning=reasoning, conflicts=conflicts)

    # --- sorting ---

    def sort_tasks_by_duration(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """
        Return tasks sorted by duration ascending (shortest first).
        Uses sorted() with a lambda key — does not modify the original list.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.duration_minutes)

    def sort_tasks_by_start_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """
        Return tasks sorted by start_time ascending ("HH:MM" string sort).
        Tasks with no start_time are placed at the end.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.start_time if t.start_time else "99:99")

    # --- filtering ---

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> list[Task]:
        """
        Return tasks matching ALL supplied filters.
        Omit a parameter to skip that filter.
        Examples:
          filter_tasks(pet_name="Buddy")            — all Buddy's tasks
          filter_tasks(completed=False)             — all incomplete tasks
          filter_tasks(pet_name="Luna", completed=True) — Luna's done tasks
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if category is not None:
            tasks = [t for t in tasks if t.category.lower() == category.lower()]
        return tasks

    # --- recurring tasks ---

    def reset_recurring_tasks(self) -> list[Task]:
        """
        For every completed recurring task, create its next occurrence and add
        it back to the correct pet. Returns the list of newly created tasks.
        Uses Task.next_occurrence() which applies timedelta internally.
        """
        new_tasks = []
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.completed and task.recurrence != "none":
                    next_task = task.next_occurrence()
                    if next_task:
                        pet.add_task(next_task)
                        new_tasks.append(next_task)
        return new_tasks

    # --- conflict detection ---

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """
        Detect scheduling conflicts among tasks that have a start_time set.
        A conflict occurs when two tasks for the same pet have overlapping
        time windows. Returns a list of warning strings (empty = no conflicts).
        Checks for overlap using: start_A < end_B and start_B < end_A.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        timed = [t for t in tasks if t.start_time]
        warnings = []

        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                # Only flag conflicts for the same pet
                if a.pet_name != b.pet_name:
                    continue
                a_start = datetime.strptime(a.start_time, "%H:%M")
                a_end   = a_start + timedelta(minutes=a.duration_minutes)
                b_start = datetime.strptime(b.start_time, "%H:%M")
                b_end   = b_start + timedelta(minutes=b.duration_minutes)

                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f'"{a.name}" ({a.start_time}–{a.end_time()}) overlaps '
                        f'"{b.name}" ({b.start_time}–{b.end_time()}) for {a.pet_name}.'
                    )
        return warnings

    # --- helpers ---

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return the reasoning string from a plan."""
        return plan.reasoning

    def get_skipped_tasks(self, plan: DailyPlan) -> list[Task]:
        """Return the list of tasks that could not be scheduled."""
        return plan.skipped

    def total_duration(self, tasks: Optional[list[Task]] = None) -> int:
        """Sum the durations of the given tasks (defaults to all owner tasks)."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sum(t.duration_minutes for t in tasks)

    def validate_constraints(self) -> list[str]:
        """
        Check for obvious problems before scheduling.
        Returns a list of warning strings (empty = all clear).
        """
        warnings = []
        if not self.owner.get_pets():
            warnings.append("No pets registered for this owner.")
        if self.owner.available_minutes <= 0:
            warnings.append("Available time is 0 minutes — nothing can be scheduled.")
        for pet in self.owner.get_pets():
            if not pet.get_tasks():
                warnings.append(f"No tasks defined for {pet.name}.")
            for task in pet.get_tasks():
                if not (1 <= task.priority <= 5):
                    warnings.append(
                        f'Task "{task.name}" for {pet.name} has an invalid priority '
                        f"({task.priority}). Must be 1-5."
                    )
                if task.duration_minutes <= 0:
                    warnings.append(
                        f'Task "{task.name}" for {pet.name} has an invalid duration '
                        f"({task.duration_minutes} min)."
                    )
        return warnings

    def _build_reasoning(
        self,
        scheduled: list[Task],
        skipped: list[Task],
        original_budget: int,
    ) -> str:
        """Compose a plain-English explanation of the scheduling decisions."""
        used = sum(t.duration_minutes for t in scheduled)
        remaining = original_budget - used
        lines = [f"{self.owner.name} has {original_budget} minutes available today."]
        if scheduled:
            names = ", ".join(f'"{t.name}"' for t in scheduled)
            lines.append(f"Scheduled ({used} min): {names}.")
        if skipped:
            for t in skipped:
                lines.append(
                    f'"{t.name}" was skipped — it needs {t.duration_minutes} min '
                    f"but only {remaining} min remained after higher-priority tasks were added."
                )
        if not scheduled:
            lines.append("No tasks could be scheduled within the available time.")
        return " ".join(lines)