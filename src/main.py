"""Main application for student-mentor assignment automation."""

import logging
import sys
import os
from typing import List, Optional

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from models.student import Student
from models.mentor import Mentor
from services.data_service import DataService
from services.assignment_service import AssignmentService
from services.export_service import ExportService
from utils.config import config


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(config.REPORTS_DIR, 'assignment.log'))
        ]
    )


class StudentMentorAssignmentSystem:
    """Main system class for student-mentor assignments."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_service = DataService()
        self.assignment_service = AssignmentService()
        self.export_service = ExportService()
    
    def run_assignment(self, create_sample_data: bool = False) -> None:
        """Run the complete assignment process."""
        try:
            self.logger.info("=" * 60)
            self.logger.info("STUDENT-MENTOR ASSIGNMENT SYSTEM STARTED")
            self.logger.info("=" * 60)
            
            # Create sample data if requested
            if create_sample_data:
                self.logger.info("Creating sample data...")
                self.data_service.create_sample_data()
            
            # Load data
            self.logger.info("Loading student and mentor data...")
            students = self.data_service.load_students()
            mentors = self.data_service.load_mentors()
            
            if not students:
                self.logger.error("No students found. Please add student data to the CSV file or use --sample-data flag.")
                return
            
            if not mentors:
                self.logger.error("No mentors found. Please add mentor data to the CSV file or use --sample-data flag.")
                return
            
            # Display initial summary
            self.display_data_summary(students, mentors)
            
            # Perform assignment
            self.logger.info("Starting assignment process...")
            summary = self.assignment_service.assign_students_to_mentors(students, mentors)
            
            # Display results
            self.display_assignment_results(summary)
            
            # Save updated data
            self.logger.info("Saving updated assignments...")
            self.data_service.save_students(students)
            self.data_service.save_mentors(mentors)
            
            # Export reports
            self.logger.info("Generating reports...")
            self.generate_reports(students, mentors, summary)
            
            self.logger.info("=" * 60)
            self.logger.info("ASSIGNMENT PROCESS COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"Error during assignment process: {str(e)}")
            raise
    
    def display_data_summary(self, students: List[Student], mentors: List[Mentor]) -> None:
        """Display summary of loaded data."""
        print("\\n" + "=" * 50)
        print("DATA SUMMARY")
        print("=" * 50)
        
        print(f"Total Students: {len(students)}")
        print(f"Total Mentors: {len(mentors)}")
        
        available_mentors = [m for m in mentors if m.availability]
        print(f"Available Mentors: {len(available_mentors)}")
        
        total_capacity = sum(m.max_students for m in available_mentors)
        print(f"Total Mentor Capacity: {total_capacity}")
        
        print(f"Batch Size: {config.BATCH_SIZE}")
        batches_needed = (len(students) + config.BATCH_SIZE - 1) // config.BATCH_SIZE
        print(f"Batches Needed: {batches_needed}")
        
        # Display student distribution by branch
        branch_count = {}
        for student in students:
            branch_count[student.branch] = branch_count.get(student.branch, 0) + 1
        
        print("\\nStudents by Branch:")
        for branch, count in sorted(branch_count.items()):
            print(f"  {branch}: {count}")
        
        # Display mentor distribution by department
        dept_count = {}
        for mentor in mentors:
            dept_count[mentor.department] = dept_count.get(mentor.department, 0) + 1
        
        print("\\nMentors by Department:")
        for dept, count in sorted(dept_count.items()):
            print(f"  {dept}: {count}")
        
        print("=" * 50)
    
    def display_assignment_results(self, summary) -> None:
        """Display assignment results."""
        print("\\n" + "=" * 50)
        print("ASSIGNMENT RESULTS")
        print("=" * 50)
        
        print(f"Total Students: {summary.total_students}")
        print(f"Total Assignments: {summary.total_assignments}")
        print(f"Average Students per Mentor: {summary.students_per_mentor_avg:.2f}")
        print(f"Unassigned Students: {len(summary.unassigned_students)}")
        
        if summary.unassigned_students:
            print(f"Unassigned Roll Numbers: {', '.join(map(str, summary.unassigned_students))}")
        
        print("\\nAssignment Details:")
        print("-" * 30)
        
        for assignment in summary.assignments:
            roll_numbers = sorted(assignment.student_roll_numbers)
            roll_range = f"{min(roll_numbers)}-{max(roll_numbers)}" if roll_numbers else "N/A"
            print(f"Batch {assignment.batch_number}: Mentor {assignment.mentor_id} -> {assignment.get_student_count()} students (Roll {roll_range})")
        
        # Calculate and display statistics
        stats = self.assignment_service.get_assignment_statistics(summary)
        print(f"\\nAssignment Efficiency: {stats['assignment_efficiency']}%")
        print(f"Mentor Utilization: {stats['mentor_utilization']}%")
        
        print("=" * 50)
    
    def generate_reports(self, students: List[Student], mentors: List[Mentor], summary) -> None:
        """Generate and save reports in multiple formats."""
        try:
            # Export summary in multiple formats
            for format_type in config.EXPORT_FORMATS:
                try:
                    file_path = self.export_service.export_assignment_summary(summary, format_type)
                    print(f"Report generated: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to export {format_type} format: {str(e)}")
            
            # Export detailed assignments
            try:
                detailed_csv = self.export_service.export_detailed_assignments(students, mentors, summary, 'csv')
                print(f"Detailed report generated: {detailed_csv}")
            except Exception as e:
                self.logger.warning(f"Failed to export detailed assignments: {str(e)}")
            
            # Export JSON for API integration
            try:
                json_file = self.export_service.export_to_json(summary)
                print(f"JSON export generated: {json_file}")
            except Exception as e:
                self.logger.warning(f"Failed to export JSON: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {str(e)}")
    
    def add_new_students_interactive(self) -> None:
        """Interactive mode to add new students."""
        print("\\n" + "=" * 50)
        print("ADD NEW STUDENTS")
        print("=" * 50)
        
        try:
            # Load existing data
            existing_students = self.data_service.load_students()
            mentors = self.data_service.load_mentors()
            
            if not existing_students:
                print("No existing assignments found. Please run initial assignment first.")
                return
            
            # Get new students from user input
            new_students = []
            while True:
                print("\\nEnter new student details (or 'done' to finish):")
                
                roll_no_input = input("Roll Number: ").strip()
                if roll_no_input.lower() == 'done':
                    break
                
                try:
                    roll_no = int(roll_no_input)
                    
                    # Check for duplicate
                    if any(s.roll_no == roll_no for s in existing_students):
                        print(f"Error: Student with roll number {roll_no} already exists!")
                        continue
                    
                    name = input("Name: ").strip()
                    branch = input("Branch: ").strip()
                    year = int(input("Year (1-4): ").strip())
                    email = input("Email (optional): ").strip() or None
                    phone = input("Phone (optional): ").strip() or None
                    
                    student = Student(roll_no, name, branch, year, email, phone)
                    new_students.append(student)
                    print(f"Added: {student}")
                    
                except ValueError as e:
                    print(f"Error: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Error adding student: {str(e)}")
                    continue
            
            if not new_students:
                print("No new students added.")
                return
            
            # Assign new students
            print(f"\\nAssigning {len(new_students)} new students...")
            summary, all_students = self.assignment_service.add_new_students(existing_students, new_students, mentors)
            
            # Display results
            self.display_assignment_results(summary)
            
            # Save updated data
            self.data_service.save_students(all_students)
            self.data_service.save_mentors(mentors)
            
            # Generate reports
            self.generate_reports(all_students, mentors, summary)
            
            print("New students added and assigned successfully!")
            
        except Exception as e:
            self.logger.error(f"Error adding new students: {str(e)}")
            print(f"Error: {str(e)}")


def main():
    """Main function."""
    setup_logging()
    
    system = StudentMentorAssignmentSystem()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if '--sample-data' in sys.argv:
            system.run_assignment(create_sample_data=True)
        elif '--add-students' in sys.argv:
            system.add_new_students_interactive()
        elif '--help' in sys.argv:
            print_help()
        else:
            print("Unknown argument. Use --help for usage information.")
    else:
        # Default: run assignment with existing data
        system.run_assignment()


def print_help():
    """Print help information."""
    print("""
Student-Mentor Assignment System

Usage:
    python main.py                 # Run assignment with existing data
    python main.py --sample-data   # Create sample data and run assignment
    python main.py --add-students  # Add new students to existing assignments
    python main.py --help         # Show this help message

Files:
    data/students.csv    # Student data file
    data/mentors.csv     # Mentor data file
    reports/            # Generated reports directory

Configuration:
    Batch size: {batch_size} students per mentor
    Assignment rules: {rules}
    
For more information, check the README.md file.
    """.format(
        batch_size=config.BATCH_SIZE,
        rules=config.ASSIGNMENT_RULES
    ))


if __name__ == "__main__":
    main()
