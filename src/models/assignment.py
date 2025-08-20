from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Assignment:
    """Assignment model representing the mentor-student assignment."""
    
    mentor_id: str
    student_roll_numbers: List[int]
    assignment_date: datetime
    batch_number: int
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate assignment data."""
        if not self.mentor_id.strip():
            raise ValueError("Mentor ID cannot be empty")
        if not self.student_roll_numbers:
            raise ValueError("Student list cannot be empty")
        if self.batch_number <= 0:
            raise ValueError("Batch number must be positive")
    
    def __str__(self):
        return f"Assignment(Mentor: {self.mentor_id}, Students: {len(self.student_roll_numbers)}, Batch: {self.batch_number})"
    
    def get_student_count(self):
        """Get number of students in this assignment."""
        return len(self.student_roll_numbers)
    
    def add_student(self, roll_no: int):
        """Add a student to this assignment."""
        if roll_no not in self.student_roll_numbers:
            self.student_roll_numbers.append(roll_no)
    
    def remove_student(self, roll_no: int):
        """Remove a student from this assignment."""
        if roll_no in self.student_roll_numbers:
            self.student_roll_numbers.remove(roll_no)
    
    def to_dict(self):
        """Convert assignment object to dictionary."""
        return {
            'mentor_id': self.mentor_id,
            'student_roll_numbers': self.student_roll_numbers.copy(),
            'assignment_date': self.assignment_date.isoformat(),
            'batch_number': self.batch_number,
            'student_count': self.get_student_count(),
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create assignment object from dictionary."""
        return cls(
            mentor_id=data['mentor_id'],
            student_roll_numbers=data['student_roll_numbers'],
            assignment_date=datetime.fromisoformat(data['assignment_date']),
            batch_number=data['batch_number'],
            notes=data.get('notes')
        )


@dataclass
class AssignmentSummary:
    """Summary of all assignments."""
    
    total_students: int
    total_mentors: int
    total_assignments: int
    students_per_mentor_avg: float
    unassigned_students: List[int]
    assignments: List[Assignment]
    created_date: datetime
    
    def __str__(self):
        return f"AssignmentSummary(Students: {self.total_students}, Mentors: {self.total_mentors}, Avg: {self.students_per_mentor_avg:.1f})"
    
    def to_dict(self):
        """Convert summary to dictionary."""
        return {
            'total_students': self.total_students,
            'total_mentors': self.total_mentors,
            'total_assignments': self.total_assignments,
            'students_per_mentor_avg': self.students_per_mentor_avg,
            'unassigned_students': self.unassigned_students.copy(),
            'assignments': [assignment.to_dict() for assignment in self.assignments],
            'created_date': self.created_date.isoformat()
        }
