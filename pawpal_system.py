from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
	def sort_by_time(self, tasks: List[Task]) -> List[Task]:
		"""Sort tasks by due time, then by pet/task ID for deterministic output.

		This keeps terminal/UI views stable when multiple tasks share the same
		due time.
		"""
		return sorted(tasks, key=lambda task: (task.due_at, task.pet_id, task.task_id))

	def detect_conflicts(self, owners: List[Owner]) -> List[str]:
		"""Detect overlapping incomplete tasks and return warning messages.

		A conflict is reported when:
		- A single pet has 2+ tasks at the same exact due time.
		- Different pets have tasks at the same exact due time.

		The method is intentionally lightweight: it never raises and always returns
		a list of human-readable warnings.
		"""
		tasks_by_due_time: dict[datetime, List[tuple[Pet, Task]]] = {}
		for owner in owners:
			for pet in owner.pets:
				for task in pet.tasks:
					if task.is_completed:
						continue
					tasks_by_due_time.setdefault(task.due_at, []).append((pet, task))

		warnings: List[str] = []
		for due_at in sorted(tasks_by_due_time.keys()):
			timed_tasks = tasks_by_due_time[due_at]
			if len(timed_tasks) < 2:
				continue

			time_label = due_at.strftime("%Y-%m-%d %H:%M")

			tasks_by_pet: dict[int, List[Task]] = {}
			pet_names: dict[int, str] = {}
			for pet, task in timed_tasks:
				tasks_by_pet.setdefault(pet.pet_id, []).append(task)
				pet_names[pet.pet_id] = pet.name

			for pet_id, pet_tasks in tasks_by_pet.items():
				if len(pet_tasks) < 2:
					continue
				titles = ", ".join(task.title for task in pet_tasks)
				warnings.append(
					f"Warning: {pet_names[pet_id]} has overlapping tasks at {time_label}: {titles}."
				)

			if len(tasks_by_pet) > 1:
				summary = ", ".join(
					f"{pet.name}: {task.title}" for pet, task in timed_tasks
				)
				warnings.append(
					f"Warning: Multiple pets have tasks at {time_label}: {summary}."
				)

		return warnings

	def _next_due_at_for_recurring_task(self, task: Task) -> Optional[datetime]:
		"""Compute the next due time for recurring tasks.

		Returns:
		- task.due_at + 1 day for "daily"
		- task.due_at + 1 week for "weekly"
		- None for all other frequencies
		"""
		frequency = task.frequency.strip().lower()
		if frequency == "daily":
			return task.due_at + timedelta(days=1)
		if frequency == "weekly":
			return task.due_at + timedelta(weeks=1)
		return None

	def _next_task_id(self, pet: Pet) -> int:
		"""Return the next available task ID for a specific pet."""
		if not pet.tasks:
			return 1
		return max(task.task_id for task in pet.tasks) + 1

	def filter_tasks(
		self,
		owners: List[Owner],
		include_completed: Optional[bool] = None,
		pet_name: Optional[str] = None,
	) -> List[Task]:
		"""Filter tasks by optional completion status and optional pet name.

		Args:
			owners: Owners to scan for tasks.
			include_completed: If True, only completed tasks are returned.
				If False, only pending tasks are returned. If None, no status filter
				is applied.
			pet_name: Case-insensitive pet name filter. If None, all pet names are
				included.

		Returns:
			A time-sorted list of matching tasks.
		"""
		normalized_pet_name = pet_name.strip().lower() if pet_name is not None else None

		filtered_tasks: List[Task] = []
		for owner in owners:
			for pet in owner.pets:
				if normalized_pet_name is not None and pet.name.lower() != normalized_pet_name:
					continue

				for task in pet.tasks:
					if include_completed is not None and task.is_completed != include_completed:
						continue
					filtered_tasks.append(task)

		return self.sort_by_time(filtered_tasks)

	def schedule(self, pet: Pet, task: Task) -> bool:
		"""Schedule a task by adding it to the provided pet."""
		return pet.add_task(task)

	def complete_task(self, pet: Pet, task_id: int) -> bool:
		"""Complete a task and auto-create the next recurring occurrence.

		Behavior:
		- Marks the matching task complete.
		- If frequency is daily/weekly, appends a new pending task with the next
		  due date.
		- Returns False when the task is missing or already completed.
		"""
		for task in pet.tasks:
			if task.task_id != task_id:
				continue

			if task.is_completed:
				return False

			task.mark_completed()
			next_due_at = self._next_due_at_for_recurring_task(task)
			if next_due_at is not None:
				next_task = Task(
					task_id=self._next_task_id(pet),
					pet_id=pet.pet_id,
					title=task.title,
					due_at=next_due_at,
					frequency=task.frequency,
				)
				pet.add_task(next_task)
			return True

		return False

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

		return self.sort_by_time(due_tasks)

	def get_all_tasks(self, owners: List[Owner], include_completed: bool = True) -> List[Task]:
		"""Return all tasks for owners sorted by due time and identifiers."""
		all_tasks: List[Task] = []
		for owner in owners:
			all_tasks.extend(owner.get_all_tasks(include_completed=include_completed))
		return self.sort_by_time(all_tasks)
