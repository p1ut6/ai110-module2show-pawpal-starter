# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial design includes five classes organized around a clear separation between data, behavior, and scheduling logic
Owner represents the person using the app. It stores their name, how many minutes they have available today, and any personal preferences (like preferring morning tasks). It holds a list of pets and exposes methods to add or retrieve them.
Pet represents the animal being cared for. It stores basic info like name, species, breed, and age, and owns the list of care tasks associated with that pet. It handles adding, removing, and retrieving tasks.
Task is a single care item — a walk, a feeding, a medication dose, etc. It stores the task name, how long it takes, a priority level (1–5), and whether it's been completed. It knows how to mark itself done, reset for a new day, and check whether it fits within a given time budget.
Scheduler is the core logic class. It takes an Owner and a Pet, reads their tasks and time constraints, and produces a prioritized daily plan. It also validates inputs and can explain in plain language why certain tasks were chosen or skipped.
DailyPlan is the output object the Scheduler produces. It holds the list of scheduled tasks, the list of skipped tasks, a reasoning string, and the date. It can serialize itself to a dict and generate a short human-readable summary.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
After asking Copilot to review the skeleton, it flagged several potential issues. The most actionable was that Task had no recurrence field, meaning daily walks and weekly grooming were treated identically to one-off tasks — a real gap for a care scheduling app. I added recurrence: str to Task to distinguish daily, weekly, and one-off tasks.
Copilot also noted that tasks had no reference back to which pet they belonged, making it hard to display tasks outside a pet context. I added a lightweight pet_name: str field rather than a full object reference, which is sufficient for display purposes without adding coupling.
I chose not to act on suggestions like multi-pet global optimization, time windows, and carryover logic. These are valid for a production app but go well beyond the scope of this project. I noted them as potential future improvements instead.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The scheduler considers two constraints: the owner's available time budget (available_minutes) and each task's priority level (1–5). Time is the hard constraint — a task simply cannot be scheduled if it doesn't fit the remaining budget. Priority is the ordering constraint — it determines which tasks get first pick of that budget. I decided time mattered most because no matter how important a task is, it can't happen if there's no time for it.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The scheduler uses a greedy algorithm: it sorts tasks by priority and picks them top-down until time runs out. The tradeoff is that this can leave time on the table — for example, two short low-priority tasks might fit in the remaining gap after one high-priority task, but a single medium-priority task that's slightly too long gets skipped entirely even though something else could fill that slot. This is reasonable for a daily pet care app because getting the most important tasks done consistently matters more than perfectly optimizing every minute.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI throughout the project for both design and code generation. The most helpful prompts were specific and structural — asking for a class skeleton based on a described scenario, asking for a review of existing code with a reference to the actual file, and asking for test cases that covered specific behaviors. Vague prompts like "build a pet app" were less useful than targeted ones like "review this skeleton for missing relationships."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
When Copilot reviewed the class skeleton, it suggested adding multi-pet global optimization, time windows, carryover logic for skipped tasks, and task dependencies. I didn't accept these as-is. I evaluated each suggestion against the project scope and decided that most of them, while valid for a production app, would significantly increase complexity without adding value for a module 2 project. I only accepted the two simplest suggestions — adding a recurrence field to Task and a pet_name field — because they were low-effort and genuinely improved the design. I verified they worked by running main.py and checking that tasks displayed their pet correctly.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested task completion (mark_complete() changes status, reset() clears it), task addition to a pet (count increases, pet_name is set automatically), task removal, owner pet management, cross-pet task retrieval, and three scheduler behaviors: respecting the time budget, prioritizing high-priority tasks, and skipping already-completed tasks. I also tested that validate_constraints() catches a zero-minute time budget. These tests mattered because the scheduler depends on all of them being correct — if get_all_tasks() or priority sorting is broken, the plan will be wrong even if the UI looks fine.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I'm confident the core scheduling logic works correctly for the tested cases. Edge cases I'd test next with more time: what happens when all tasks have equal priority, when available time exactly matches the total duration of all tasks, when a pet has no tasks but another pet does, and when the owner has only one minute available.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The separation between the logic layer (pawpal_system.py) and the UI (app.py) worked really well. Because all the scheduling logic lived in plain Python classes, the Streamlit app stayed thin and mostly just called methods — it didn't need to know anything about how tasks were sorted or selected. That made debugging much easier.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add a way to save and load data between sessions — right now everything resets when you close the browser. I'd also improve the scheduler to consider filling leftover time with lower-priority tasks rather than leaving gaps, and add recurring task support so daily tasks automatically reset each day.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The most important thing I learned is that AI is most useful as a collaborator when you already have a clear enough understanding of the problem to evaluate what it suggests. When I gave Copilot a well-structured file and a specific question, the feedback was actionable. When I accepted suggestions without thinking critically about scope, I would have ended up overbuilding. The judgment about what to keep and what to skip is still yours to make.