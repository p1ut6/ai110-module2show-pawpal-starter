"""
app.py
PawPal+ — Streamlit UI
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state — initialise once, persist across reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_owner() -> Owner:
    return st.session_state.owner

# ---------------------------------------------------------------------------
# Sidebar — owner setup
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🐾 PawPal+")
    st.subheader("Owner setup")

    with st.form("owner_form"):
        owner_name = st.text_input("Your name", placeholder="e.g. Alex")
        avail = st.number_input("Available minutes today", min_value=1, max_value=480, value=90)
        submitted = st.form_submit_button("Save owner")
        if submitted and owner_name.strip():
            existing_pets = get_owner()._pets if get_owner() else []
            new_owner = Owner(name=owner_name.strip(), available_minutes=int(avail))
            for pet in existing_pets:
                new_owner.add_pet(pet)
            st.session_state.owner = new_owner
            st.success(f"Saved! Hi {owner_name} 👋")

    if get_owner():
        st.caption(f"Owner: **{get_owner().name}** · {get_owner().available_minutes} min available")

# ---------------------------------------------------------------------------
# Guard — require owner before showing anything else
# ---------------------------------------------------------------------------

if not get_owner():
    st.info("👈 Enter your name in the sidebar to get started.")
    st.stop()

owner = get_owner()

# ---------------------------------------------------------------------------
# Main area — tabs
# ---------------------------------------------------------------------------

tab_pets, tab_tasks, tab_plan = st.tabs(["🐶 My Pets", "📋 Tasks", "📅 Today's Plan"])

# ── Tab 1: Pets ─────────────────────────────────────────────────────────────

with tab_pets:
    st.header("My Pets")

    with st.form("add_pet_form"):
        st.subheader("Add a pet")
        col1, col2 = st.columns(2)
        with col1:
            pet_name    = st.text_input("Pet name", placeholder="e.g. Buddy")
            pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        with col2:
            pet_breed = st.text_input("Breed (optional)", placeholder="e.g. Labrador")
            pet_age   = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        add_pet = st.form_submit_button("Add pet")

    if add_pet:
        if not pet_name.strip():
            st.warning("Please enter a pet name.")
        else:
            existing_names = [p.name.lower() for p in owner.get_pets()]
            if pet_name.strip().lower() in existing_names:
                st.warning(f"You already have a pet named {pet_name}.")
            else:
                new_pet = Pet(
                    name=pet_name.strip(),
                    species=pet_species,
                    breed=pet_breed.strip(),
                    age=int(pet_age),
                )
                owner.add_pet(new_pet)
                st.success(f"Added {new_pet.name} 🐾")

    pets = owner.get_pets()
    if not pets:
        st.info("No pets added yet. Use the form above to add one.")
    else:
        for pet in pets:
            with st.expander(f"{pet.name} — {pet.species} ({len(pet.get_tasks())} tasks)"):
                st.write(f"**Breed:** {pet.breed or '—'}  |  **Age:** {pet.age} yr")
                tasks = pet.get_tasks()
                if tasks:
                    for t in tasks:
                        status = "✅" if t.completed else "⬜"
                        time_str = f" @ {t.start_time}" if t.start_time else ""
                        st.write(f"{status} {t.name} · {t.duration_minutes} min · priority {t.priority}{time_str}")
                else:
                    st.caption("No tasks yet — add some in the Tasks tab.")

# ── Tab 2: Tasks ────────────────────────────────────────────────────────────

with tab_tasks:
    st.header("Tasks")

    pets = owner.get_pets()
    if not pets:
        st.warning("Add a pet first before adding tasks.")
    else:
        with st.form("add_task_form"):
            st.subheader("Add a task")
            col1, col2 = st.columns(2)
            with col1:
                selected_pet    = st.selectbox("Pet", [p.name for p in pets])
                task_name       = st.text_input("Task name", placeholder="e.g. Morning walk")
                task_cat        = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
                task_start_time = st.text_input("Start time (optional)", placeholder="e.g. 09:00")
            with col2:
                task_duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
                task_priority   = st.slider("Priority", min_value=1, max_value=5, value=3,
                                            help="1 = low, 5 = must-do")
                task_recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])
            add_task = st.form_submit_button("Add task")

        if add_task:
            if not task_name.strip():
                st.warning("Please enter a task name.")
            else:
                # Validate start time format if provided
                start_time = task_start_time.strip()
                if start_time:
                    try:
                        from datetime import datetime
                        datetime.strptime(start_time, "%H:%M")
                    except ValueError:
                        st.error("Start time must be in HH:MM format, e.g. 09:00")
                        st.stop()

                pet_obj = next(p for p in pets if p.name == selected_pet)
                new_task = Task(
                    name=task_name.strip(),
                    duration_minutes=int(task_duration),
                    priority=int(task_priority),
                    category=task_cat,
                    recurrence=task_recurrence,
                    start_time=start_time,
                )
                pet_obj.add_task(new_task)
                st.success(f"Added '{new_task.name}' to {pet_obj.name}.")

        st.subheader("All tasks")
        all_tasks = owner.get_all_tasks()
        if not all_tasks:
            st.info("No tasks yet.")
        else:
            for pet in pets:
                for task in pet.get_tasks():
                    col1, col2, col3 = st.columns([4, 2, 2])
                    with col1:
                        time_str = f" @ {task.start_time}" if task.start_time else ""
                        st.write(f"**{task.name}** ({pet.name}) · {task.category}{time_str}")
                    with col2:
                        st.write(f"{task.duration_minutes} min · ⭐ {task.priority}")
                    with col3:
                        if st.button("✅ Done" if not task.completed else "↩ Reset",
                                     key=f"toggle_{task.task_id}"):
                            if task.completed:
                                task.reset()
                            else:
                                task.mark_complete()
                            st.rerun()

# ── Tab 3: Today's Plan ──────────────────────────────────────────────────────

with tab_plan:
    st.header("Today's Plan")

    scheduler = Scheduler(owner)
    warnings  = scheduler.validate_constraints()

    if warnings:
        for w in warnings:
            st.warning(w)

    if st.button("🗓 Generate plan", type="primary"):
        if not owner.get_all_tasks():
            st.warning("Add some tasks first.")
        else:
            plan = scheduler.generate_plan()
            st.session_state.plan = plan

    if "plan" in st.session_state:
        plan = st.session_state.plan

        # Summary metrics
        total_min = sum(t.duration_minutes for t in plan.tasks)
        col1, col2, col3 = st.columns(3)
        col1.metric("Scheduled", f"{len(plan.tasks)} tasks")
        col2.metric("Total time", f"{total_min} min")
        col3.metric("Skipped", f"{len(plan.skipped)} tasks")

        # Conflict warnings
        if plan.conflicts:
            st.subheader("⚠️ Conflicts detected")
            for c in plan.conflicts:
                st.warning(c)

        # Scheduled tasks
        st.subheader("✅ Scheduled")
        if plan.tasks:
            for t in plan.tasks:
                time_str = f" @ {t.start_time}–{t.end_time()}" if t.start_time else ""
                st.write(f"**[{t.priority}★] {t.name}** ({t.pet_name}) · {t.duration_minutes} min · {t.category}{time_str}")
        else:
            st.info("No tasks could be scheduled.")

        # Skipped tasks
        if plan.skipped:
            st.subheader("⏭ Skipped")
            for t in plan.skipped:
                st.write(f"{t.name} ({t.pet_name}) · needed {t.duration_minutes} min · priority {t.priority}")

        # Reasoning
        st.subheader("💡 Reasoning")
        st.info(plan.reasoning)