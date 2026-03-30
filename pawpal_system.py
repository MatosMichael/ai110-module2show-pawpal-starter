from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
	task_id: int
	pet_id: int
	title: str
	due_at: datetime
	frequency: str = "once"
	is_completed: bool = False

	def mark_completed(self) -> None:
		"""Mark this task as completed."""
		self.is_completed = True

	def reschedule(self, new_due_at: datetime) -> None:
		"""Update the due date and time for this task."""
		self.due_at = new_due_at


@dataclass
class Pet:
	pet_id: int
	name: str
	species: str
	age: int
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> bool:
		"""Add a task for this pet when IDs match and task ID is unique."""
		if task.pet_id != self.pet_id:
			return False

		if any(existing.task_id == task.task_id for existing in self.tasks):
			return False

		self.tasks.append(task)
		return True

	def complete_task(self, task_id: int) -> bool:
		"""Mark the matching task as completed for this pet."""
		for task in self.tasks:
			if task.task_id == task_id:
				task.mark_completed()
				return True
		return False


@dataclass
class Owner:
	owner_id: int
	name: str
	email: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner if it is not already present."""
		if self.get_pet(pet.pet_id) is None:
			self.pets.append(pet)

	def remove_pet(self, pet_id: int) -> bool:
		"""Remove a pet by ID and return whether removal occurred."""
		for i, pet in enumerate(self.pets):
			if pet.pet_id == pet_id:
				del self.pets[i]
				return True
		return False

	def get_pet(self, pet_id: int) -> Optional[Pet]:
		"""Return the pet with the given ID, or None if missing."""
		for pet in self.pets:
			if pet.pet_id == pet_id:
				return pet
		return None

	def get_all_tasks(self, include_completed: bool = True) -> List[Task]:
		"""Collect tasks across all pets, optionally filtering completed ones."""
		tasks: List[Task] = []
		for pet in self.pets:
			for task in pet.tasks:
				if include_completed or not task.is_completed:
					tasks.append(task)
		return tasks


class Scheduler:
	def schedule(self, pet: Pet, task: Task) -> bool:
		"""Schedule a task by adding it to the provided pet."""
		return pet.add_task(task)

	def cancel(self, pet: Pet, task_id: int) -> bool:
		"""Cancel and remove a task from a pet by task ID."""
		for i, task in enumerate(pet.tasks):
			if task.task_id == task_id:
				del pet.tasks[i]
				return True
		return False

	def get_due_tasks(self, owners: List[Owner], now: Optional[datetime] = None) -> List[Task]:
		"""Return incomplete tasks due at or before the given time."""
		if now is None:
			now = datetime.now()

		due_tasks: List[Task] = []
		for owner in owners:
			for task in owner.get_all_tasks(include_completed=False):
				if task.due_at <= now:
					due_tasks.append(task)

		return sorted(due_tasks, key=lambda task: (task.due_at, task.pet_id, task.task_id))

	def get_all_tasks(self, owners: List[Owner], include_completed: bool = True) -> List[Task]:
		"""Return all tasks for owners sorted by due time and identifiers."""
		all_tasks: List[Task] = []
		for owner in owners:
			all_tasks.extend(owner.get_all_tasks(include_completed=include_completed))
		return sorted(all_tasks, key=lambda task: (task.due_at, task.pet_id, task.task_id))
