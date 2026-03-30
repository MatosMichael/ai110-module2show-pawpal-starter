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

	tasks = [
		Task(
			task_id=1,
			pet_id=dog.pet_id,
			title="Morning Walk",
			due_at=now.replace(hour=8, minute=0, second=0, microsecond=0),
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
			task_id=3,
			pet_id=dog.pet_id,
			title="Evening Medication",
			due_at=now.replace(hour=19, minute=0, second=0, microsecond=0) + timedelta(minutes=15),
			frequency="daily",
		),
	]

	for task in tasks:
		pet = owner.get_pet(task.pet_id)
		if pet is not None:
			scheduler.schedule(pet, task)

	return owner, scheduler


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
	print("Today's Schedule")
	print("-" * 40)

	tasks = scheduler.get_all_tasks([owner], include_completed=False)
	if not tasks:
		print("No tasks scheduled for today.")
		return

	for task in tasks:
		pet = owner.get_pet(task.pet_id)
		pet_name = pet.name if pet is not None else f"Pet {task.pet_id}"
		time_str = task.due_at.strftime("%I:%M %p")
		print(f"{time_str} | {pet_name:<10} | {task.title} ({task.frequency})")


def main() -> None:
	owner, scheduler = build_sample_data()
	print_todays_schedule(owner, scheduler)


if __name__ == "__main__":
	main()
