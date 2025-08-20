"""Assignment service for handling student-mentor assignments."""

import logging
import os
import sys
from datetime import datetime
from typing import List, Tuple, Dict, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.mentor import Mentor
from models.assignment import Assignment, AssignmentSummary
from utils.config import config
from utils.validators import validate_data_consistency, AssignmentValidator


class AssignmentService:
    """Service for handling student-mentor assignments."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def assign_students_to_mentors(self, students: List[Student], mentors: List[Mentor]) -> AssignmentSummary:
        """
        Assign students to mentors using batch allocation algorithm.
        
        Algorithm:
        1. Sort students by roll number (if configured)
        2. Filter available mentors
        3. Create batches of students (default: 30 per batch)
        4. Assign each batch to a mentor sequentially
        5. Handle remainder students in the last batch
        """
        self.logger.info(f"Starting assignment process for {len(students)} students and {len(mentors)} mentors")
        
        # Validate input data
        is_valid, issues = validate_data_consistency(students, mentors)
        if not is_valid:
            self.logger.error(f"Data validation failed: {issues}")
            raise ValueError(f"Data validation failed: {'; '.join(issues)}")
        
        # Sort students by roll number if configured
        if config.ASSIGNMENT_RULES['sort_by_roll_number']:
            students = sorted(students, key=lambda s: s.roll_no)
            self.logger.info("Students sorted by roll number")
        
        # Filter available mentors
        available_mentors = [m for m in mentors if m.availability]
        if not available_mentors:
            raise ValueError("No available mentors found")
        
        self.logger.info(f"Found {len(available_mentors)} available mentors")
        
        # Reset mentor assignments
        for mentor in available_mentors:
            mentor.assigned_students = []
        
        # Create assignments
        assignments = []
        unassigned_students = []
        batch_size = config.BATCH_SIZE
        
        # Calculate number of complete batches and remainder
        complete_batches = len(students) // batch_size
        remainder_students_count = len(students) % batch_size
        
        self.logger.info(f"Creating {complete_batches} complete batches of {batch_size} students each")
        if remainder_students_count > 0:
            self.logger.info(f"Remainder: {remainder_students_count} students")
        
        current_mentor_index = 0
        
        # Process complete batches first
        for batch_num in range(complete_batches):
            # Calculate batch boundaries
            start_idx = batch_num * batch_size
            end_idx = start_idx + batch_size
            batch_students = students[start_idx:end_idx]
            
            self.logger.info(f"Processing batch {batch_num + 1}: students {start_idx + 1}-{end_idx}")
            
            # Handle case where we need more mentors than available
            if current_mentor_index >= len(available_mentors):
                if config.ASSIGNMENT_RULES['wrap_around_mentors']:
                    current_mentor_index = 0  # Start over
                    self.logger.warning("Wrapping around mentors - some mentors will have multiple batches")
                else:
                    # Add remaining students to unassigned list
                    unassigned_students.extend(batch_students)
                    self.logger.warning(f"No more mentors available. {len(batch_students)} students remain unassigned")
                    continue
            
            # Get current mentor
            current_mentor = available_mentors[current_mentor_index]
            
            # Create assignment
            student_roll_numbers = [s.roll_no for s in batch_students]
            assignment = Assignment(
                mentor_id=current_mentor.faculty_id,
                student_roll_numbers=student_roll_numbers,
                assignment_date=datetime.now(),
                batch_number=batch_num + 1,
                notes=f"Batch assignment with {len(batch_students)} students"
            )
            
            # Update mentor
            current_mentor.assigned_students.extend(student_roll_numbers)
            
            # Update students
            for student in batch_students:
                student.assigned_mentor_id = current_mentor.faculty_id
            
            assignments.append(assignment)
            self.logger.info(f"Assigned {len(batch_students)} students to mentor {current_mentor.faculty_id}")
            
            # Move to next mentor
            current_mentor_index += 1
        
        # Handle remainder students
        if remainder_students_count > 0:
            start_idx = complete_batches * batch_size
            remainder_students = students[start_idx:]
            
            self.logger.info(f"Processing remainder: {remainder_students_count} students (Roll {start_idx + 1}-{len(students)})")
            
            if remainder_students_count <= config.ASSIGNMENT_RULES['remainder_threshold']:
                # Add remainder students to the last assigned mentor
                if assignments:
                    last_assignment = assignments[-1]
                    last_mentor = next(m for m in available_mentors if m.faculty_id == last_assignment.mentor_id)
                    
                    # Check if adding remainder students exceeds mentor capacity
                    total_after_addition = len(last_assignment.student_roll_numbers) + remainder_students_count
                    if total_after_addition > last_mentor.max_students and not config.ASSIGNMENT_RULES['allow_mentor_overload']:
                        unassigned_students.extend(remainder_students)
                        self.logger.warning(f"Cannot add {remainder_students_count} students to mentor {last_mentor.faculty_id} - would exceed capacity")
                    else:
                        # Add remainder students to last mentor
                        remainder_roll_numbers = [s.roll_no for s in remainder_students]
                        last_assignment.student_roll_numbers.extend(remainder_roll_numbers)
                        last_mentor.assigned_students.extend(remainder_roll_numbers)
                        
                        # Update students
                        for student in remainder_students:
                            student.assigned_mentor_id = last_mentor.faculty_id
                        
                        # Update assignment notes
                        last_assignment.notes = f"Batch assignment with {len(last_assignment.student_roll_numbers)} students (includes {remainder_students_count} remainder students)"
                        
                        if total_after_addition > last_mentor.max_students:
                            self.logger.warning(f"Mentor {last_mentor.faculty_id} now has {total_after_addition} students (exceeds normal capacity of {last_mentor.max_students})")
                        
                        self.logger.info(f"Added {remainder_students_count} remainder students to mentor {last_mentor.faculty_id}")
                else:
                    # No previous assignments, treat as regular batch
                    unassigned_students.extend(remainder_students)
                    self.logger.warning("No previous assignments to add remainder students to")
            else:
                # Remainder > remainder_threshold, assign to new mentor
                self.logger.info(f"Remainder students ({remainder_students_count}) > {config.ASSIGNMENT_RULES['remainder_threshold']}, assigning to new mentor")
                
                if current_mentor_index < len(available_mentors):
                    current_mentor = available_mentors[current_mentor_index]
                    
                    # Create new assignment for remainder students
                    remainder_roll_numbers = [s.roll_no for s in remainder_students]
                    assignment = Assignment(
                        mentor_id=current_mentor.faculty_id,
                        student_roll_numbers=remainder_roll_numbers,
                        assignment_date=datetime.now(),
                        batch_number=complete_batches + 1,
                        notes=f"Remainder batch assignment with {remainder_students_count} students"
                    )
                    
                    # Update mentor
                    current_mentor.assigned_students.extend(remainder_roll_numbers)
                    
                    # Update students
                    for student in remainder_students:
                        student.assigned_mentor_id = current_mentor.faculty_id
                    
                    assignments.append(assignment)
                    self.logger.info(f"Assigned {remainder_students_count} remainder students to new mentor {current_mentor.faculty_id}")
                else:
                    # No more mentors available
                    unassigned_students.extend(remainder_students)
                    self.logger.warning(f"No more mentors available for {remainder_students_count} remainder students")
        
        # Create summary
        summary = self._create_assignment_summary(students, mentors, assignments, unassigned_students)
        
        self.logger.info(f"Assignment completed: {len(assignments)} assignments created, {len(unassigned_students)} students unassigned")
        return summary
    
    def _create_assignment_summary(self, students: List[Student], mentors: List[Mentor], 
                                 assignments: List[Assignment], unassigned_students: List[Student]) -> AssignmentSummary:
        """Create a summary of the assignment process."""
        total_assigned = sum(len(assignment.student_roll_numbers) for assignment in assignments)
        avg_students_per_mentor = total_assigned / len(assignments) if assignments else 0
        
        unassigned_roll_numbers = [s.roll_no for s in unassigned_students]
        
        return AssignmentSummary(
            total_students=len(students),
            total_mentors=len(mentors),
            total_assignments=len(assignments),
            students_per_mentor_avg=avg_students_per_mentor,
            unassigned_students=unassigned_roll_numbers,
            assignments=assignments,
            created_date=datetime.now()
        )
    
    def reassign_students(self, students: List[Student], mentors: List[Mentor], 
                         mentor_to_remove: str = None) -> AssignmentSummary:
        """Reassign students, optionally removing a specific mentor."""
        self.logger.info(f"Starting reassignment process")
        
        if mentor_to_remove:
            # Mark mentor as unavailable
            for mentor in mentors:
                if mentor.faculty_id == mentor_to_remove:
                    mentor.availability = False
                    mentor.assigned_students = []
                    self.logger.info(f"Removed mentor {mentor_to_remove} from assignments")
                    break
        
        # Clear all existing assignments
        for student in students:
            student.assigned_mentor_id = None
        
        for mentor in mentors:
            mentor.assigned_students = []
        
        # Perform new assignment
        return self.assign_students_to_mentors(students, mentors)
    
    def add_new_students(self, existing_students: List[Student], new_students: List[Student], 
                        mentors: List[Mentor]) -> Tuple[AssignmentSummary, List[Student]]:
        """Add new students to existing assignments."""
        self.logger.info(f"Adding {len(new_students)} new students to existing assignments")
        
        # Validate new students
        for student in new_students:
            if any(s.roll_no == student.roll_no for s in existing_students):
                raise ValueError(f"Student with roll number {student.roll_no} already exists")
        
        # Sort new students by roll number
        if config.ASSIGNMENT_RULES['sort_by_roll_number']:
            new_students = sorted(new_students, key=lambda s: s.roll_no)
        
        # Find mentors with available capacity
        available_mentors = []
        for mentor in mentors:
            if mentor.availability and mentor.get_available_slots() > 0:
                available_mentors.append((mentor, mentor.get_available_slots()))
        
        # Sort mentors by available slots (ascending) to balance load
        available_mentors.sort(key=lambda x: x[1])
        
        assigned_students = []
        unassigned_students = new_students.copy()
        
        # Try to assign to mentors with available capacity first
        for mentor, available_slots in available_mentors:
            if not unassigned_students:
                break
            
            can_assign = min(available_slots, len(unassigned_students))
            students_to_assign = unassigned_students[:can_assign]
            
            for student in students_to_assign:
                student.assigned_mentor_id = mentor.faculty_id
                mentor.assign_student(student.roll_no)
                assigned_students.append(student)
            
            unassigned_students = unassigned_students[can_assign:]
            self.logger.info(f"Assigned {can_assign} new students to mentor {mentor.faculty_id}")
        
        # If there are still unassigned students and overload is allowed
        if unassigned_students and config.ASSIGNMENT_RULES['allow_mentor_overload']:
            available_mentors_for_overload = [m for m in mentors if m.availability]
            
            if available_mentors_for_overload:
                # Assign remaining students to the first available mentor
                mentor = available_mentors_for_overload[0]
                
                for student in unassigned_students:
                    student.assigned_mentor_id = mentor.faculty_id
                    mentor.assign_student(student.roll_no)
                    assigned_students.append(student)
                
                self.logger.warning(f"Assigned {len(unassigned_students)} additional students to mentor {mentor.faculty_id} (overload)")
                unassigned_students = []
        
        # Combine all students
        all_students = existing_students + assigned_students + unassigned_students
        
        # Create new summary
        current_assignments = self._extract_current_assignments(all_students, mentors)
        summary = self._create_assignment_summary(all_students, mentors, current_assignments, unassigned_students)
        
        return summary, all_students
    
    def _extract_current_assignments(self, students: List[Student], mentors: List[Mentor]) -> List[Assignment]:
        """Extract current assignments from student and mentor data."""
        assignments = []
        
        for i, mentor in enumerate(mentors):
            if mentor.assigned_students:
                assignment = Assignment(
                    mentor_id=mentor.faculty_id,
                    student_roll_numbers=mentor.assigned_students.copy(),
                    assignment_date=datetime.now(),
                    batch_number=i + 1,
                    notes=f"Current assignment with {len(mentor.assigned_students)} students"
                )
                assignments.append(assignment)
        
        return assignments
    
    def get_assignment_statistics(self, summary: AssignmentSummary) -> Dict[str, Any]:
        """Generate detailed statistics about the assignment."""
        stats = {
            'total_students': summary.total_students,
            'total_mentors': summary.total_mentors,
            'total_assignments': summary.total_assignments,
            'students_per_mentor_avg': round(summary.students_per_mentor_avg, 2),
            'unassigned_count': len(summary.unassigned_students),
            'assignment_efficiency': round((summary.total_students - len(summary.unassigned_students)) / summary.total_students * 100, 2) if summary.total_students > 0 else 0,
            'mentor_utilization': round(summary.total_assignments / summary.total_mentors * 100, 2) if summary.total_mentors > 0 else 0,
            'batch_details': []
        }
        
        # Add batch details
        for assignment in summary.assignments:
            batch_info = {
                'batch_number': assignment.batch_number,
                'mentor_id': assignment.mentor_id,
                'student_count': assignment.get_student_count(),
                'student_roll_range': f"{min(assignment.student_roll_numbers)}-{max(assignment.student_roll_numbers)}" if assignment.student_roll_numbers else "N/A"
            }
            stats['batch_details'].append(batch_info)
        
        return stats
