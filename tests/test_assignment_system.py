"""Test suite for the student-mentor assignment system."""

import unittest
import tempfile
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.student import Student
from models.mentor import Mentor
from models.assignment import Assignment, AssignmentSummary
from services.data_service import DataService
from services.assignment_service import AssignmentService
from utils.validators import StudentValidator, MentorValidator, validate_data_consistency


class TestStudentModel(unittest.TestCase):
    """Test cases for Student model."""
    
    def test_student_creation(self):
        """Test student object creation."""
        student = Student(1, "John Doe", "CSE", 2, "john@example.com", "1234567890")
        
        self.assertEqual(student.roll_no, 1)
        self.assertEqual(student.name, "John Doe")
        self.assertEqual(student.branch, "CSE")
        self.assertEqual(student.year, 2)
        self.assertEqual(student.email, "john@example.com")
        self.assertEqual(student.phone, "1234567890")
        self.assertIsNone(student.assigned_mentor_id)
    
    def test_student_validation(self):
        """Test student validation."""
        # Valid student
        with self.assertRaises(ValueError):
            Student(0, "John Doe", "CSE", 2)  # Invalid roll number
        
        with self.assertRaises(ValueError):
            Student(1, "", "CSE", 2)  # Empty name
        
        with self.assertRaises(ValueError):
            Student(1, "John Doe", "CSE", 5)  # Invalid year
    
    def test_student_sorting(self):
        """Test student sorting by roll number."""
        students = [
            Student(3, "Alice", "CSE", 1),
            Student(1, "Bob", "ECE", 1),
            Student(2, "Carol", "MECH", 1)
        ]
        
        sorted_students = sorted(students)
        self.assertEqual([s.roll_no for s in sorted_students], [1, 2, 3])


class TestMentorModel(unittest.TestCase):
    """Test cases for Mentor model."""
    
    def test_mentor_creation(self):
        """Test mentor object creation."""
        mentor = Mentor("FAC001", "Dr. Smith", "Computer Science", "smith@example.com", "9876543210")
        
        self.assertEqual(mentor.faculty_id, "FAC001")
        self.assertEqual(mentor.name, "Dr. Smith")
        self.assertEqual(mentor.department, "Computer Science")
        self.assertTrue(mentor.availability)
        self.assertEqual(mentor.max_students, 30)
        self.assertEqual(len(mentor.assigned_students), 0)
    
    def test_mentor_student_assignment(self):
        """Test assigning students to mentor."""
        mentor = Mentor("FAC001", "Dr. Smith", "Computer Science")
        
        # Test assignment
        mentor.assign_student(101)
        self.assertIn(101, mentor.assigned_students)
        self.assertEqual(mentor.get_student_count(), 1)
        
        # Test capacity check
        self.assertTrue(mentor.can_accept_students())
        self.assertEqual(mentor.get_available_slots(), 29)
        
        # Test removal
        mentor.remove_student(101)
        self.assertNotIn(101, mentor.assigned_students)
        self.assertEqual(mentor.get_student_count(), 0)


class TestAssignmentService(unittest.TestCase):
    """Test cases for Assignment Service."""
    
    def setUp(self):
        """Set up test data."""
        self.students = [
            Student(i, f"Student {i}", "CSE", 1) for i in range(1, 65)
        ]
        
        self.mentors = [
            Mentor(f"FAC{i:03d}", f"Dr. Mentor {i}", "Computer Science") 
            for i in range(1, 4)
        ]
        
        self.assignment_service = AssignmentService()
    
    def test_basic_assignment(self):
        """Test basic student-mentor assignment."""
        summary = self.assignment_service.assign_students_to_mentors(self.students, self.mentors)
        
        self.assertEqual(summary.total_students, 64)
        self.assertEqual(summary.total_mentors, 3)
        self.assertEqual(summary.total_assignments, 3)
        
        # Check that all students except remainder are assigned
        total_assigned = sum(len(assignment.student_roll_numbers) for assignment in summary.assignments)
        self.assertGreater(total_assigned, 0)
        
        # Check batch sizes
        for i, assignment in enumerate(summary.assignments):
            if i < 2:  # First two batches should have 30 students
                self.assertEqual(assignment.get_student_count(), 30)
            else:  # Last batch should have remaining students
                self.assertEqual(assignment.get_student_count(), 4)  # 64 - 60 = 4
    
    def test_assignment_with_insufficient_mentors(self):
        """Test assignment when there are insufficient mentors."""
        # Create many students with few mentors
        many_students = [Student(i, f"Student {i}", "CSE", 1) for i in range(1, 101)]
        few_mentors = [Mentor("FAC001", "Dr. Mentor 1", "Computer Science")]
        
        summary = self.assignment_service.assign_students_to_mentors(many_students, few_mentors)
        
        # Should handle the case gracefully
        self.assertIsInstance(summary, AssignmentSummary)
    
    def test_add_new_students(self):
        """Test adding new students to existing assignments."""
        # First, create initial assignments
        initial_summary = self.assignment_service.assign_students_to_mentors(self.students, self.mentors)
        
        # Add new students
        new_students = [Student(i, f"New Student {i}", "CSE", 1) for i in range(101, 106)]
        
        updated_summary, all_students = self.assignment_service.add_new_students(
            self.students, new_students, self.mentors
        )
        
        self.assertEqual(len(all_students), 64 + 5)  # Original + new students
        self.assertIsInstance(updated_summary, AssignmentSummary)


class TestValidators(unittest.TestCase):
    """Test cases for validation utilities."""
    
    def test_student_validator(self):
        """Test student data validation."""
        valid_student_data = {
            'roll_no': '123',
            'name': 'John Doe',
            'branch': 'CSE',
            'year': '2',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        is_valid, errors = StudentValidator.validate_student(valid_student_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test invalid data
        invalid_student_data = {
            'roll_no': 'invalid',
            'name': '',
            'branch': 'CSE',
            'year': '5'
        }
        
        is_valid, errors = StudentValidator.validate_student(invalid_student_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_mentor_validator(self):
        """Test mentor data validation."""
        valid_mentor_data = {
            'faculty_id': 'FAC001',
            'name': 'Dr. Smith',
            'department': 'Computer Science',
            'email': 'smith@example.com',
            'phone': '9876543210'
        }
        
        is_valid, errors = MentorValidator.validate_mentor(valid_mentor_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test invalid data
        invalid_mentor_data = {
            'faculty_id': '',
            'name': '',
            'department': 'Computer Science'
        }
        
        is_valid, errors = MentorValidator.validate_mentor(invalid_mentor_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestDataService(unittest.TestCase):
    """Test cases for Data Service."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.data_service = DataService()
    
    def test_create_sample_data(self):
        """Test creating sample data."""
        students, mentors = self.data_service.create_sample_data()
        
        self.assertGreater(len(students), 0)
        self.assertGreater(len(mentors), 0)
        
        # Verify students are properly created
        for student in students:
            self.assertIsInstance(student, Student)
            self.assertGreater(student.roll_no, 0)
            self.assertTrue(student.name)
        
        # Verify mentors are properly created
        for mentor in mentors:
            self.assertIsInstance(mentor, Mentor)
            self.assertTrue(mentor.faculty_id)
            self.assertTrue(mentor.name)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_classes = [
        TestStudentModel,
        TestMentorModel,
        TestAssignmentService,
        TestValidators,
        TestDataService
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
