from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
	task_id: int
	title: str
	due_at: datetime
	is_completed: bool = False

	def mark_completed(self) -> None:
		pass

	def reschedule(self, new_due_at: datetime) -> None:
		pass


@dataclass
class Pet:
	pet_id: int
	name: str
	species: str
	age: int
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		pass

	def complete_task(self, task_id: int) -> None:
		pass


@dataclass
class Owner:
	owner_id: int
	name: str
	email: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		pass

	def remove_pet(self, pet_id: int) -> None:
		pass


class Scheduler:
	def __init__(self) -> None:
		self.tasks: List[Task] = []

	def schedule(self, task: Task) -> None:
		pass

	def cancel(self, task_id: int) -> None:
		pass

	def get_due_tasks(self, now: Optional[datetime] = None) -> List[Task]:
		pass
