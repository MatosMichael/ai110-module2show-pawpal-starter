from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_get_all_tasks_returns_tasks_in_chronological_order() -> None:
	owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")
	pet = Pet(pet_id=10, name="Mochi", species="dog", age=3)
	owner.add_pet(pet)

	now = datetime.now().replace(second=0, microsecond=0)
	late_task = Task(task_id=10, pet_id=10, title="Evening walk", due_at=now + timedelta(hours=3))
	early_task = Task(task_id=11, pet_id=10, title="Breakfast", due_at=now + timedelta(minutes=30))
	middle_task = Task(task_id=12, pet_id=10, title="Medication", due_at=now + timedelta(hours=1))

	pet.add_task(late_task)
	pet.add_task(early_task)
	pet.add_task(middle_task)

	scheduler = Scheduler()
	sorted_tasks = scheduler.get_all_tasks([owner])

	assert [task.task_id for task in sorted_tasks] == [11, 12, 10]


def test_filter_tasks_by_completion_status() -> None:
	owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")
	pet = Pet(pet_id=10, name="Mochi", species="cat", age=3)
	owner.add_pet(pet)

	completed_task = Task(
		task_id=1,
		pet_id=10,
		title="Breakfast",
		due_at=datetime.now() + timedelta(minutes=30),
	)
	completed_task.mark_completed()

	pending_task = Task(
		task_id=2,
		pet_id=10,
		title="Evening play",
		due_at=datetime.now() + timedelta(hours=2),
	)

	pet.add_task(completed_task)
	pet.add_task(pending_task)

	scheduler = Scheduler()
	filtered = scheduler.filter_tasks([owner], include_completed=False)

	assert len(filtered) == 1
	assert filtered[0].task_id == pending_task.task_id


def test_filter_tasks_by_pet_name() -> None:
	owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")
	dog = Pet(pet_id=10, name="Mochi", species="dog", age=3)
	cat = Pet(pet_id=20, name="Luna", species="cat", age=5)
	owner.add_pet(dog)
	owner.add_pet(cat)

	dog_task = Task(
		task_id=1,
		pet_id=10,
		title="Morning walk",
		due_at=datetime.now() + timedelta(minutes=20),
	)
	cat_task = Task(
		task_id=2,
		pet_id=20,
		title="Feed Luna",
		due_at=datetime.now() + timedelta(minutes=10),
	)

	dog.add_task(dog_task)
	cat.add_task(cat_task)

	scheduler = Scheduler()
	filtered = scheduler.filter_tasks([owner], pet_name="luna")

	assert len(filtered) == 1
	assert filtered[0].task_id == cat_task.task_id


def test_complete_daily_task_creates_next_occurrence() -> None:
	pet = Pet(pet_id=10, name="Mochi", species="dog", age=3)
	due_at = datetime.now()
	task = Task(
		task_id=1,
		pet_id=10,
		title="Morning walk",
		due_at=due_at,
		frequency="daily",
	)
	pet.add_task(task)

	scheduler = Scheduler()
	completed = scheduler.complete_task(pet, 1)

	assert completed is True
	assert len(pet.tasks) == 2
	assert pet.tasks[0].is_completed is True

	next_task = pet.tasks[1]
	assert next_task.title == "Morning walk"
	assert next_task.frequency == "daily"
	assert next_task.is_completed is False
	assert next_task.due_at == due_at + timedelta(days=1)


def test_complete_weekly_task_creates_next_occurrence() -> None:
	pet = Pet(pet_id=20, name="Luna", species="cat", age=5)
	due_at = datetime.now()
	task = Task(
		task_id=7,
		pet_id=20,
		title="Grooming",
		due_at=due_at,
		frequency="weekly",
	)
	pet.add_task(task)

	scheduler = Scheduler()
	completed = scheduler.complete_task(pet, 7)

	assert completed is True
	assert len(pet.tasks) == 2
	assert pet.tasks[0].is_completed is True
	assert pet.tasks[1].due_at == due_at + timedelta(weeks=1)


def test_complete_one_time_task_does_not_create_next_occurrence() -> None:
	pet = Pet(pet_id=30, name="Bean", species="cat", age=2)
	task = Task(
		task_id=4,
		pet_id=30,
		title="Vet check",
		due_at=datetime.now(),
		frequency="once",
	)
	pet.add_task(task)

	scheduler = Scheduler()
	completed = scheduler.complete_task(pet, 4)

	assert completed is True
	assert len(pet.tasks) == 1
	assert pet.tasks[0].is_completed is True


def test_detect_conflicts_returns_warning_for_same_pet_and_multi_pet_overlap() -> None:
	owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")
	dog = Pet(pet_id=10, name="Mochi", species="dog", age=3)
	cat = Pet(pet_id=20, name="Luna", species="cat", age=5)
	owner.add_pet(dog)
	owner.add_pet(cat)

	overlap_time = datetime.now().replace(second=0, microsecond=0)
	dog.add_task(Task(task_id=1, pet_id=10, title="Walk", due_at=overlap_time))
	dog.add_task(Task(task_id=2, pet_id=10, title="Medication", due_at=overlap_time))
	cat.add_task(Task(task_id=3, pet_id=20, title="Feed", due_at=overlap_time))

	scheduler = Scheduler()
	warnings = scheduler.detect_conflicts([owner])

	assert any("Mochi has overlapping tasks" in warning for warning in warnings)
	assert any("Multiple pets have tasks" in warning for warning in warnings)


def test_detect_conflicts_flags_duplicate_task_times_for_same_pet() -> None:
	owner = Owner(owner_id=3, name="Alex", email="alex@example.com")
	pet = Pet(pet_id=99, name="Nova", species="dog", age=4)
	owner.add_pet(pet)

	duplicate_time = datetime.now().replace(second=0, microsecond=0)
	pet.add_task(Task(task_id=1, pet_id=99, title="Walk", due_at=duplicate_time))
	pet.add_task(Task(task_id=2, pet_id=99, title="Feed", due_at=duplicate_time))

	scheduler = Scheduler()
	warnings = scheduler.detect_conflicts([owner])

	assert len(warnings) == 1
	assert "Nova has overlapping tasks" in warnings[0]


def test_detect_conflicts_returns_empty_for_non_overlapping_tasks() -> None:
	owner = Owner(owner_id=2, name="Sam", email="sam@example.com")
	pet = Pet(pet_id=30, name="Bean", species="cat", age=2)
	owner.add_pet(pet)

	now = datetime.now().replace(second=0, microsecond=0)
	pet.add_task(Task(task_id=1, pet_id=30, title="Play", due_at=now))
	pet.add_task(Task(task_id=2, pet_id=30, title="Brush", due_at=now + timedelta(hours=1)))

	scheduler = Scheduler()
	assert scheduler.detect_conflicts([owner]) == []
