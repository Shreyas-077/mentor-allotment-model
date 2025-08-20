"""Data service for handling CSV file operations."""

import csv
import os
import logging
from typing import List, Dict, Any, Optional
import sys

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.mentor import Mentor
from utils.config import config
from utils.validators import ValidationError, StudentValidator, MentorValidator


class DataService:
    """Service for handling data operations (CSV files)."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        config.ensure_directories_exist()
    
    def load_students(self, file_path: Optional[str] = None) -> List[Student]:
        """Load students from CSV file."""
        file_path = file_path or config.STUDENTS_FILE
        students = []
        
        if not os.path.exists(file_path):
            self.logger.warning(f"Students file not found: {file_path}")
            return students
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is row 1)
                    try:
                        # Validate row data
                        is_valid, errors = StudentValidator.validate_student(row)
                        if not is_valid:
                            self.logger.error(f"Invalid student data at row {row_num}: {errors}")
                            continue
                        
                        student = Student.from_dict(row)
                        students.append(student)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing student at row {row_num}: {str(e)}")
                        continue
            
            self.logger.info(f"Loaded {len(students)} students from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error reading students file: {str(e)}")
            raise
        
        return students
    
    def load_mentors(self, file_path: Optional[str] = None) -> List[Mentor]:
        """Load mentors from CSV file."""
        file_path = file_path or config.MENTORS_FILE
        mentors = []
        
        if not os.path.exists(file_path):
            self.logger.warning(f"Mentors file not found: {file_path}")
            return mentors
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Convert string 'True'/'False' to boolean
                        if 'availability' in row:
                            row['availability'] = row['availability'].lower() in ['true', '1', 'yes']
                        
                        # Convert max_students to int if present
                        if 'max_students' in row and row['max_students']:
                            row['max_students'] = int(row['max_students'])
                        
                        # Validate row data
                        is_valid, errors = MentorValidator.validate_mentor(row)
                        if not is_valid:
                            self.logger.error(f"Invalid mentor data at row {row_num}: {errors}")
                            continue
                        
                        mentor = Mentor.from_dict(row)
                        mentors.append(mentor)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing mentor at row {row_num}: {str(e)}")
                        continue
            
            self.logger.info(f"Loaded {len(mentors)} mentors from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error reading mentors file: {str(e)}")
            raise
        
        return mentors
    
    def save_students(self, students: List[Student], file_path: Optional[str] = None):
        """Save students to CSV file."""
        file_path = file_path or config.STUDENTS_FILE
        
        if not students:
            self.logger.warning("No students to save")
            return
        
        try:
            fieldnames = ['roll_no', 'name', 'branch', 'year', 'email', 'phone', 'assigned_mentor_id']
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for student in students:
                    writer.writerow(student.to_dict())
            
            self.logger.info(f"Saved {len(students)} students to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving students file: {str(e)}")
            raise
    
    def save_mentors(self, mentors: List[Mentor], file_path: Optional[str] = None):
        """Save mentors to CSV file."""
        file_path = file_path or config.MENTORS_FILE
        
        if not mentors:
            self.logger.warning("No mentors to save")
            return
        
        try:
            fieldnames = ['faculty_id', 'name', 'department', 'email', 'phone', 'availability', 'max_students']
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for mentor in mentors:
                    mentor_dict = mentor.to_dict()
                    # Remove assigned_students and current_student_count for CSV storage
                    mentor_dict.pop('assigned_students', None)
                    mentor_dict.pop('current_student_count', None)
                    writer.writerow(mentor_dict)
            
            self.logger.info(f"Saved {len(mentors)} mentors to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving mentors file: {str(e)}")
            raise
    
    def create_sample_data(self):
        """Create sample data files for testing."""
        self.logger.info("Creating sample data files...")
        
        # Sample students
        sample_students = []
        branches = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE']
        
        for i in range(1, 65):  # 64 students to test remainder logic
            student = Student(
                roll_no=i,
                name=f"Student {i:02d}",
                branch=branches[(i-1) % len(branches)],
                year=((i-1) // 16) + 1,  # Distribute across years
                email=f"student{i:02d}@university.edu",
                phone=f"98765{i:05d}"
            )
            sample_students.append(student)
        
        # Sample mentors
        sample_mentors = []
        departments = ['Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Electrical']
        
        for i in range(1, 4):  # 3 mentors to test assignment logic
            mentor = Mentor(
                faculty_id=f"FAC{i:03d}",
                name=f"Dr. Mentor {i}",
                department=departments[(i-1) % len(departments)],
                email=f"mentor{i}@university.edu",
                phone=f"87654{i:05d}",
                availability=True,
                max_students=30
            )
            sample_mentors.append(mentor)
        
        # Save sample data
        self.save_students(sample_students)
        self.save_mentors(sample_mentors)
        
        self.logger.info("Sample data created successfully!")
        return sample_students, sample_mentors
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of current data."""
        try:
            students = self.load_students()
            mentors = self.load_mentors()
            
            available_mentors = [m for m in mentors if m.availability]
            total_capacity = sum(m.max_students for m in available_mentors)
            
            return {
                'total_students': len(students),
                'total_mentors': len(mentors),
                'available_mentors': len(available_mentors),
                'total_capacity': total_capacity,
                'capacity_utilization': len(students) / total_capacity if total_capacity > 0 else 0,
                'students_file_exists': os.path.exists(config.STUDENTS_FILE),
                'mentors_file_exists': os.path.exists(config.MENTORS_FILE)
            }
        except Exception as e:
            self.logger.error(f"Error getting data summary: {str(e)}")
            return {}
