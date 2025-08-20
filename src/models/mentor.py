from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Mentor:
    """Mentor model representing a faculty/mentor entity."""
    
    faculty_id: str
    name: str
    department: str
    email: Optional[str] = None
    phone: Optional[str] = None
    availability: bool = True
    max_students: int = 30
    assigned_students: List[int] = None  # List of student roll numbers
    
    def __post_init__(self):
        """Initialize assigned_students list and validate data."""
        if self.assigned_students is None:
            self.assigned_students = []
        
        if not self.faculty_id.strip():
            raise ValueError("Faculty ID cannot be empty")
        if not self.name.strip():
            raise ValueError("Mentor name cannot be empty")
        if self.max_students <= 0:
            raise ValueError("Max students must be positive")
    
    def __str__(self):
        return f"Mentor(ID: {self.faculty_id}, Name: {self.name}, Department: {self.department})"
    
    def get_student_count(self):
        """Get current number of assigned students."""
        return len(self.assigned_students)
    
    def can_accept_students(self, count=1):
        """Check if mentor can accept more students."""
        return self.availability and (self.get_student_count() + count <= self.max_students)
    
    def assign_student(self, student_roll_no: int):
        """Assign a student to this mentor."""
        if not self.can_accept_students():
            raise ValueError(f"Mentor {self.faculty_id} cannot accept more students")
        
        if student_roll_no not in self.assigned_students:
            self.assigned_students.append(student_roll_no)
    
    def remove_student(self, student_roll_no: int):
        """Remove a student from this mentor."""
        if student_roll_no in self.assigned_students:
            self.assigned_students.remove(student_roll_no)
    
    def get_available_slots(self):
        """Get number of available slots for new students."""
        return max(0, self.max_students - self.get_student_count())
    
    def to_dict(self):
        """Convert mentor object to dictionary."""
        return {
            'faculty_id': self.faculty_id,
            'name': self.name,
            'department': self.department,
            'email': self.email,
            'phone': self.phone,
            'availability': self.availability,
            'max_students': self.max_students,
            'assigned_students': self.assigned_students.copy(),
            'current_student_count': self.get_student_count()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create mentor object from dictionary."""
        return cls(
            faculty_id=data['faculty_id'],
            name=data['name'],
            department=data['department'],
            email=data.get('email'),
            phone=data.get('phone'),
            availability=data.get('availability', True),
            max_students=data.get('max_students', 30),
            assigned_students=data.get('assigned_students', [])
        )
