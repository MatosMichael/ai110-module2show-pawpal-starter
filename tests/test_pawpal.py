from datetime import datetime, timedelta

from pawpal_system import Pet, Task


def test_mark_completed_changes_task_status() -> None:
	task = Task(
		task_id=1,
		pet_id=10,
		title="Feed breakfast",
		due_at=datetime.now() + timedelta(hours=1),
	)

	assert task.is_completed is False

	task.mark_completed()

	assert task.is_completed is True


def test_add_task_increases_pet_task_count() -> None:
	pet = Pet(pet_id=10, name="Mochi", species="cat", age=3)
	task = Task(
		task_id=2,
		pet_id=10,
		title="Evening play",
		due_at=datetime.now() + timedelta(hours=2),
	)

	starting_count = len(pet.tasks)

	added = pet.add_task(task)

	assert added is True
	assert len(pet.tasks) == starting_count + 1
