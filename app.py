import streamlit as st
from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")

# Keep one Owner object in the session vault; only create it if missing/invalid.
if "owner" not in st.session_state or not isinstance(st.session_state["owner"], Owner):
    st.session_state["owner"] = Owner(owner_id=1, name=owner_name, email="owner@example.com")
else:
    st.session_state["owner"].name = owner_name

if "scheduler" not in st.session_state or not isinstance(st.session_state["scheduler"], Scheduler):
    st.session_state["scheduler"] = Scheduler()

if "next_pet_id" not in st.session_state:
    st.session_state["next_pet_id"] = 1

if "next_task_id" not in st.session_state:
    st.session_state["next_task_id"] = 1

st.markdown("### Add Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Pet age", min_value=0, max_value=40, value=2)

if st.button("Add pet"):
    new_pet = Pet(
        pet_id=st.session_state["next_pet_id"],
        name=pet_name,
        species=species,
        age=int(age),
    )
    existing_pet_names = {pet.name.lower() for pet in st.session_state["owner"].pets}
    if pet_name.strip().lower() in existing_pet_names:
        st.info(f"{pet_name} is already in this owner's pet list.")
    else:
        st.session_state["owner"].add_pet(new_pet)
        st.session_state["next_pet_id"] += 1
        st.success(f"Added pet {pet_name}.")

if st.session_state["owner"].pets:
    st.write("Current pets:")
    st.table(
        [
            {"pet_id": pet.pet_id, "name": pet.name, "species": pet.species, "age": pet.age}
            for pet in st.session_state["owner"].pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Schedule tasks for one of the owner's pets.")

pet_options = {f"{pet.name} (id={pet.pet_id})": pet.pet_id for pet in st.session_state["owner"].pets}
selected_pet_label = st.selectbox("Choose pet", list(pet_options.keys()), disabled=not pet_options)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if not pet_options:
        st.warning("Add at least one pet before scheduling tasks.")
    else:
        selected_pet_id = pet_options[selected_pet_label]
        selected_pet = st.session_state["owner"].get_pet(selected_pet_id)
        if selected_pet is None:
            st.error("Selected pet was not found.")
        else:
            due_at = datetime.now() + timedelta(minutes=int(duration))
            task = Task(
                task_id=st.session_state["next_task_id"],
                pet_id=selected_pet.pet_id,
                title=f"{task_title} ({priority})",
                due_at=due_at,
            )
            if st.session_state["scheduler"].schedule(selected_pet, task):
                st.session_state["next_task_id"] += 1
                st.success(f"Scheduled '{task_title}' for {selected_pet.name}.")
            else:
                st.error("Could not schedule this task.")

all_tasks = st.session_state["owner"].get_all_tasks(include_completed=True)
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "task_id": task.task_id,
                "pet_id": task.pet_id,
                "title": task.title,
                "due_at": task.due_at.strftime("%Y-%m-%d %H:%M"),
                "is_completed": task.is_completed,
            }
            for task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Shows tasks currently due, based on your Scheduler logic.")

if st.button("Generate schedule"):
    due_tasks = st.session_state["scheduler"].get_due_tasks([st.session_state["owner"]])
    if due_tasks:
        st.write("Tasks due now:")
        st.table(
            [
                {
                    "task_id": task.task_id,
                    "pet_id": task.pet_id,
                    "title": task.title,
                    "due_at": task.due_at.strftime("%Y-%m-%d %H:%M"),
                }
                for task in due_tasks
            ]
        )
    else:
        st.info("No tasks are due yet.")
