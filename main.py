from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def build_sample_data() -> tuple[Owner, Scheduler]:
	owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")

	dog = Pet(pet_id=101, name="Mochi", species="dog", age=3)
	cat = Pet(pet_id=202, name="Luna", species="cat", age=5)

	owner.add_pet(dog)
	owner.add_pet(cat)

	now = datetime.now()
	scheduler = Scheduler()

	# Intentionally out of order to demonstrate sorting behavior.
	tasks = [
		Task(
			task_id=3,
			pet_id=dog.pet_id,
			title="Evening Medication",
			due_at=now.replace(hour=19, minute=0, second=0, microsecond=0) + timedelta(minutes=15),
			frequency="daily",
		),
		Task(
			task_id=2,
			pet_id=cat.pet_id,
			title="Feed Luna",
			due_at=now.replace(hour=12, minute=30, second=0, microsecond=0),
			frequency="daily",
		),
		Task(
			task_id=4,
			pet_id=dog.pet_id,
			title="Noon Training",
			due_at=now.replace(hour=12, minute=30, second=0, microsecond=0),
			frequency="daily",
		),
		Task(
			task_id=5,
			pet_id=dog.pet_id,
			title="Lunch Medication",
			due_at=now.replace(hour=12, minute=30, second=0, microsecond=0),
			frequency="daily",
		),
		Task(
			task_id=1,
			pet_id=dog.pet_id,
			title="Morning Walk",
			due_at=now.replace(hour=8, minute=0, second=0, microsecond=0),
			frequency="daily",
		),
	]

	for task in tasks:
		pet = owner.get_pet(task.pet_id)
		if pet is not None:
			scheduler.schedule(pet, task)

	# Mark one task as completed so completion filtering can be demonstrated.
	owner.get_pet(cat.pet_id).complete_task(2)

	return owner, scheduler


def print_tasks(title: str, owner: Owner, tasks: list[Task]) -> None:
	print(title)
	print("-" * 40)

	if not tasks:
		print("No tasks found.")
		return

	for task in tasks:
		pet = owner.get_pet(task.pet_id)
		pet_name = pet.name if pet is not None else f"Pet {task.pet_id}"
		time_str = task.due_at.strftime("%I:%M %p")
		status = "done" if task.is_completed else "pending"
		print(f"{time_str} | {pet_name:<10} | {task.title:<20} | {status}")


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
	all_tasks = owner.get_all_tasks(include_completed=True)
	print_tasks("Raw Task Entry Order (for comparison)", owner, all_tasks)

	sorted_tasks = scheduler.sort_by_time(all_tasks)
	print_tasks("Sorted by Time", owner, sorted_tasks)

	pending_tasks = scheduler.filter_tasks([owner], include_completed=False)
	print_tasks("Pending Tasks Only", owner, pending_tasks)

	luna_tasks = scheduler.filter_tasks([owner], pet_name="Luna")
	print_tasks("Tasks for Luna (pet_name filter)", owner, luna_tasks)

	print("Conflict Warnings")
	print("-" * 40)
	conflicts = scheduler.detect_conflicts([owner])
	if not conflicts:
		print("No conflicts found.")
	else:
		for warning in conflicts:
			print(warning)


def main() -> None:
	owner, scheduler = build_sample_data()
	print_todays_schedule(owner, scheduler)


if __name__ == "__main__":
	main()
