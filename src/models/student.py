from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    """Student model representing a student entity."""
    
    roll_no: int
    name: str
    branch: str
    year: int
    email: Optional[str] = None
    phone: Optional[str] = None
    assigned_mentor_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate student data after initialization."""
        if self.roll_no <= 0:
            raise ValueError("Roll number must be positive")
        if not self.name.strip():
            raise ValueError("Student name cannot be empty")
        if self.year not in [1, 2, 3, 4]:
            raise ValueError("Year must be between 1 and 4")
    
    def __str__(self):
        return f"Student(Roll: {self.roll_no}, Name: {self.name}, Branch: {self.branch})"
    
    def __lt__(self, other):
        """Enable sorting by roll number."""
        return self.roll_no < other.roll_no
    
    def to_dict(self):
        """Convert student object to dictionary."""
        return {
            'roll_no': self.roll_no,
            'name': self.name,
            'branch': self.branch,
            'year': self.year,
            'email': self.email,
            'phone': self.phone,
            'assigned_mentor_id': self.assigned_mentor_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create student object from dictionary."""
        return cls(
            roll_no=int(data['roll_no']),
            name=data['name'],
            branch=data['branch'],
            year=int(data['year']),
            email=data.get('email'),
            phone=data.get('phone'),
            assigned_mentor_id=data.get('assigned_mentor_id')
        )
