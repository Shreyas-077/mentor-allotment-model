"""Validation utilities for the student-mentor assignment system."""

import re
import os
import sys
from typing import List, Dict, Any, Tuple

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.mentor import Mentor
from utils.config import config


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class StudentValidator:
    """Validator for student data."""
    
    @staticmethod
    def validate_roll_number(roll_no: int) -> bool:
        """Validate student roll number."""
        min_roll = config.VALIDATION_RULES['min_roll_number']
        max_roll = config.VALIDATION_RULES['max_roll_number']
        return min_roll <= roll_no <= max_roll
    
    @staticmethod
    def validate_year(year: int) -> bool:
        """Validate student academic year."""
        return year in config.VALIDATION_RULES['valid_years']
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return True  # Email is optional
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return True  # Phone is optional
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return 10 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_student(student_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete student data."""
        errors = []
        
        # Check required fields
        required_fields = config.VALIDATION_RULES['required_student_fields']
        for field in required_fields:
            if field not in student_data or not student_data[field]:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate roll number
        try:
            roll_no = int(student_data['roll_no'])
            if not StudentValidator.validate_roll_number(roll_no):
                errors.append(f"Roll number {roll_no} is out of valid range")
        except (ValueError, TypeError):
            errors.append("Roll number must be a valid integer")
        
        # Validate year
        try:
            year = int(student_data['year'])
            if not StudentValidator.validate_year(year):
                errors.append(f"Year {year} is not valid")
        except (ValueError, TypeError):
            errors.append("Year must be a valid integer")
        
        # Validate name
        if not student_data['name'].strip():
            errors.append("Student name cannot be empty")
        
        # Validate optional fields
        if 'email' in student_data and student_data['email']:
            if not StudentValidator.validate_email(student_data['email']):
                errors.append("Invalid email format")
        
        if 'phone' in student_data and student_data['phone']:
            if not StudentValidator.validate_phone(student_data['phone']):
                errors.append("Invalid phone number format")
        
        return len(errors) == 0, errors


class MentorValidator:
    """Validator for mentor data."""
    
    @staticmethod
    def validate_faculty_id(faculty_id: str) -> bool:
        """Validate faculty ID format."""
        return bool(faculty_id and faculty_id.strip())
    
    @staticmethod
    def validate_mentor(mentor_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete mentor data."""
        errors = []
        
        # Check required fields
        required_fields = config.VALIDATION_RULES['required_mentor_fields']
        for field in required_fields:
            if field not in mentor_data or not mentor_data[field]:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate faculty ID
        if not MentorValidator.validate_faculty_id(mentor_data['faculty_id']):
            errors.append("Faculty ID cannot be empty")
        
        # Validate name
        if not mentor_data['name'].strip():
            errors.append("Mentor name cannot be empty")
        
        # Validate department
        if not mentor_data['department'].strip():
            errors.append("Department cannot be empty")
        
        # Validate optional fields
        if 'email' in mentor_data and mentor_data['email']:
            if not StudentValidator.validate_email(mentor_data['email']):
                errors.append("Invalid email format")
        
        if 'phone' in mentor_data and mentor_data['phone']:
            if not StudentValidator.validate_phone(mentor_data['phone']):
                errors.append("Invalid phone number format")
        
        if 'max_students' in mentor_data:
            try:
                max_students = int(mentor_data['max_students'])
                if max_students <= 0:
                    errors.append("Max students must be positive")
            except (ValueError, TypeError):
                errors.append("Max students must be a valid integer")
        
        return len(errors) == 0, errors


class AssignmentValidator:
    """Validator for assignment logic."""
    
    @staticmethod
    def validate_assignment_feasibility(students: List[Student], mentors: List[Mentor]) -> Tuple[bool, List[str]]:
        """Validate if assignment is feasible with given students and mentors."""
        errors = []
        warnings = []
        
        if not students:
            errors.append("No students to assign")
        
        if not mentors:
            errors.append("No mentors available")
        
        if errors:
            return False, errors
        
        # Check for duplicate roll numbers
        roll_numbers = [s.roll_no for s in students]
        if len(roll_numbers) != len(set(roll_numbers)):
            errors.append("Duplicate roll numbers found in student list")
        
        # Check for duplicate faculty IDs
        faculty_ids = [m.faculty_id for m in mentors]
        if len(faculty_ids) != len(set(faculty_ids)):
            errors.append("Duplicate faculty IDs found in mentor list")
        
        # Check capacity
        total_capacity = sum(m.max_students for m in mentors if m.availability)
        total_students = len(students)
        
        if total_students > total_capacity:
            if not config.ASSIGNMENT_RULES['allow_mentor_overload']:
                errors.append(f"Not enough mentor capacity. Students: {total_students}, Capacity: {total_capacity}")
            else:
                warnings.append(f"Some mentors will exceed normal capacity. Students: {total_students}, Capacity: {total_capacity}")
        
        # Check if we have enough mentors for batch assignment
        available_mentors = [m for m in mentors if m.availability]
        batches_needed = (total_students + config.BATCH_SIZE - 1) // config.BATCH_SIZE
        
        if batches_needed > len(available_mentors):
            if not config.ASSIGNMENT_RULES['wrap_around_mentors']:
                errors.append(f"Not enough mentors for batch assignment. Need: {batches_needed}, Available: {len(available_mentors)}")
        
        return len(errors) == 0, errors + warnings
    
    @staticmethod
    def validate_batch_assignment(batch_students: List[Student], mentor: Mentor) -> Tuple[bool, List[str]]:
        """Validate a specific batch assignment."""
        errors = []
        
        if not batch_students:
            errors.append("Empty batch cannot be assigned")
        
        if not mentor.availability:
            errors.append(f"Mentor {mentor.faculty_id} is not available")
        
        if len(batch_students) > mentor.max_students:
            if not config.ASSIGNMENT_RULES['allow_mentor_overload']:
                errors.append(f"Batch size {len(batch_students)} exceeds mentor capacity {mentor.max_students}")
        
        return len(errors) == 0, errors


def validate_data_consistency(students: List[Student], mentors: List[Mentor]) -> Tuple[bool, List[str]]:
    """Validate overall data consistency."""
    all_issues = []
    
    # Validate individual students
    for student in students:
        try:
            student_dict = student.to_dict()
            is_valid, errors = StudentValidator.validate_student(student_dict)
            if not is_valid:
                all_issues.extend([f"Student {student.roll_no}: {error}" for error in errors])
        except Exception as e:
            all_issues.append(f"Student {student.roll_no}: {str(e)}")
    
    # Validate individual mentors
    for mentor in mentors:
        try:
            mentor_dict = mentor.to_dict()
            is_valid, errors = MentorValidator.validate_mentor(mentor_dict)
            if not is_valid:
                all_issues.extend([f"Mentor {mentor.faculty_id}: {error}" for error in errors])
        except Exception as e:
            all_issues.append(f"Mentor {mentor.faculty_id}: {str(e)}")
    
    # Validate assignment feasibility
    is_feasible, feasibility_issues = AssignmentValidator.validate_assignment_feasibility(students, mentors)
    all_issues.extend(feasibility_issues)
    
    return len(all_issues) == 0, all_issues
