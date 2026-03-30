from dataclasses import dataclass
from typing import List


@dataclass
class Pet:
    """Represents a pet with name and type."""
    pet_name: str
    pet_type: str
    breed: str = ""
    
    def edit_pet(self) -> None:
        """Edit pet information."""
        pass


@dataclass
class FeedingTimes:
    """Represents a feeding schedule for a pet."""
    food_type: str
    time: str
    
    def set_time(self) -> None:
        """Set the feeding time."""
        pass


@dataclass
class ScheduleWalk:
    """Represents a walk schedule for a pet."""
    walk_length: int
    frequency: int
    
    def set_time(self) -> None:
        """Set the walk time."""
        pass


class Owner:
    """Represents a pet owner managing their pets."""
    
    def __init__(self, owner_name: str, contact: str):
        """Initialize an owner with name and contact information."""
        self.owner_name: str = owner_name
        self.contact: str = contact
        self.pets: List[Pet] = []
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        pass
    
    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's collection."""
        pass
