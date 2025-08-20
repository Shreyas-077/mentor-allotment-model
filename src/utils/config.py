"""Configuration settings for the student-mentor assignment system."""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the application."""
    
    # Data settings
    BATCH_SIZE = 30  # Number of students per mentor
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    
    STUDENTS_FILE = os.path.join(DATA_DIR, 'students.csv')
    MENTORS_FILE = os.path.join(DATA_DIR, 'mentors.csv')
    ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'assignments.csv')
    
    # Export settings
    EXPORT_FORMATS = ['csv', 'excel', 'pdf']
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Assignment rules
    ASSIGNMENT_RULES = {
        'strict_batch_size': False,  # If True, reject if not enough mentors for all students
        'allow_mentor_overload': True,  # If True, last mentor can have more than BATCH_SIZE
        'sort_by_roll_number': True,  # Sort students by roll number before assignment
        'wrap_around_mentors': False,  # If True and more students than mentor capacity, reuse mentors
        'remainder_threshold': 12,  # If remainder <= this value, add to last mentor; else create new assignment
    }
    
    # Validation rules
    VALIDATION_RULES = {
        'min_roll_number': 1,
        'max_roll_number': 9999,
        'valid_years': [1, 2, 3, 4],
        'required_student_fields': ['roll_no', 'name', 'branch', 'year'],
        'required_mentor_fields': ['faculty_id', 'name', 'department'],
    }
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all configuration settings as a dictionary."""
        return {
            'batch_size': cls.BATCH_SIZE,
            'data_dir': cls.DATA_DIR,
            'reports_dir': cls.REPORTS_DIR,
            'export_formats': cls.EXPORT_FORMATS,
            'assignment_rules': cls.ASSIGNMENT_RULES,
            'validation_rules': cls.VALIDATION_RULES
        }
    
    @classmethod
    def update_batch_size(cls, new_size: int):
        """Update the batch size setting."""
        if new_size <= 0:
            raise ValueError("Batch size must be positive")
        cls.BATCH_SIZE = new_size
    
    @classmethod
    def ensure_directories_exist(cls):
        """Ensure all required directories exist."""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration."""
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""
    LOG_LEVEL = 'WARNING'
    ASSIGNMENT_RULES = {
        'strict_batch_size': True,
        'allow_mentor_overload': False,
        'sort_by_roll_number': True,
        'wrap_around_mentors': True,
    }


# Default configuration
config = Config()
