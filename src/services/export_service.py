"""Export service for generating reports in various formats."""

import csv
import json
import os
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.assignment import AssignmentSummary
from models.student import Student
from models.mentor import Mentor
from utils.config import config

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ExportService:
    """Service for exporting assignment data to various formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        config.ensure_directories_exist()
    
    def export_assignment_summary(self, summary: AssignmentSummary, format_type: str = 'csv', 
                                filename: Optional[str] = None) -> str:
        """Export assignment summary to specified format."""
        if format_type not in config.EXPORT_FORMATS:
            raise ValueError(f"Unsupported format: {format_type}. Supported formats: {config.EXPORT_FORMATS}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if filename is None:
            filename = f"assignment_summary_{timestamp}"
        
        if format_type == 'csv':
            return self._export_to_csv(summary, filename)
        elif format_type == 'excel':
            return self._export_to_excel(summary, filename)
        elif format_type == 'pdf':
            return self._export_to_pdf(summary, filename)
        else:
            raise ValueError(f"Format {format_type} not implemented")
    
    def _export_to_csv(self, summary: AssignmentSummary, filename: str) -> str:
        """Export assignment summary to CSV format."""
        base_path = os.path.join(config.REPORTS_DIR, f"{filename}.csv")
        
        try:
            with open(base_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write summary header
                writer.writerow(['Assignment Summary Report'])
                writer.writerow(['Generated on:', summary.created_date.strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                # Write summary statistics
                writer.writerow(['Summary Statistics'])
                writer.writerow(['Total Students:', summary.total_students])
                writer.writerow(['Total Mentors:', summary.total_mentors])
                writer.writerow(['Total Assignments:', summary.total_assignments])
                writer.writerow(['Average Students per Mentor:', f"{summary.students_per_mentor_avg:.2f}"])
                writer.writerow(['Unassigned Students:', len(summary.unassigned_students)])
                writer.writerow([])
                
                # Write assignments details
                writer.writerow(['Assignment Details'])
                writer.writerow(['Batch Number', 'Mentor ID', 'Student Count', 'Student Roll Numbers'])
                
                for assignment in summary.assignments:
                    roll_numbers = ', '.join(map(str, sorted(assignment.student_roll_numbers)))
                    writer.writerow([
                        assignment.batch_number,
                        assignment.mentor_id,
                        assignment.get_student_count(),
                        roll_numbers
                    ])
                
                # Write unassigned students if any
                if summary.unassigned_students:
                    writer.writerow([])
                    writer.writerow(['Unassigned Students'])
                    writer.writerow(['Roll Numbers:', ', '.join(map(str, summary.unassigned_students))])
            
            self.logger.info(f"Assignment summary exported to CSV: {base_path}")
            return base_path
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def _export_to_excel(self, summary: AssignmentSummary, filename: str) -> str:
        """Export assignment summary to Excel format."""
        if not PANDAS_AVAILABLE:
            self.logger.warning("Pandas not available. Falling back to CSV export.")
            return self._export_to_csv(summary, filename)
        
        base_path = os.path.join(config.REPORTS_DIR, f"{filename}.xlsx")
        
        try:
            with pd.ExcelWriter(base_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Students',
                        'Total Mentors', 
                        'Total Assignments',
                        'Average Students per Mentor',
                        'Unassigned Students',
                        'Generation Date'
                    ],
                    'Value': [
                        summary.total_students,
                        summary.total_mentors,
                        summary.total_assignments,
                        f"{summary.students_per_mentor_avg:.2f}",
                        len(summary.unassigned_students),
                        summary.created_date.strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Assignments sheet
                assignments_data = []
                for assignment in summary.assignments:
                    assignments_data.append({
                        'Batch Number': assignment.batch_number,
                        'Mentor ID': assignment.mentor_id,
                        'Student Count': assignment.get_student_count(),
                        'Student Roll Numbers': ', '.join(map(str, sorted(assignment.student_roll_numbers))),
                        'Assignment Date': assignment.assignment_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                if assignments_data:
                    assignments_df = pd.DataFrame(assignments_data)
                    assignments_df.to_excel(writer, sheet_name='Assignments', index=False)
                
                # Unassigned students sheet
                if summary.unassigned_students:
                    unassigned_df = pd.DataFrame({
                        'Unassigned Roll Numbers': summary.unassigned_students
                    })
                    unassigned_df.to_excel(writer, sheet_name='Unassigned', index=False)
            
            self.logger.info(f"Assignment summary exported to Excel: {base_path}")
            return base_path
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            raise
    
    def _export_to_pdf(self, summary: AssignmentSummary, filename: str) -> str:
        """Export assignment summary to PDF format."""
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available. Falling back to CSV export.")
            return self._export_to_csv(summary, filename)
        
        base_path = os.path.join(config.REPORTS_DIR, f"{filename}.pdf")
        
        try:
            doc = SimpleDocTemplate(base_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Student-Mentor Assignment Report", title_style))
            story.append(Spacer(1, 20))
            
            # Summary section
            story.append(Paragraph("Summary Statistics", styles['Heading2']))
            summary_data = [
                ['Metric', 'Value'],
                ['Total Students', str(summary.total_students)],
                ['Total Mentors', str(summary.total_mentors)],
                ['Total Assignments', str(summary.total_assignments)],
                ['Average Students per Mentor', f"{summary.students_per_mentor_avg:.2f}"],
                ['Unassigned Students', str(len(summary.unassigned_students))],
                ['Generated on', summary.created_date.strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 30))
            
            # Assignments section
            if summary.assignments:
                story.append(Paragraph("Assignment Details", styles['Heading2']))
                
                assignments_data = [['Batch', 'Mentor ID', 'Students', 'Roll Number Range']]
                
                for assignment in summary.assignments:
                    roll_numbers = sorted(assignment.student_roll_numbers)
                    roll_range = f"{min(roll_numbers)}-{max(roll_numbers)}" if roll_numbers else "N/A"
                    
                    assignments_data.append([
                        str(assignment.batch_number),
                        assignment.mentor_id,
                        str(assignment.get_student_count()),
                        roll_range
                    ])
                
                assignments_table = Table(assignments_data)
                assignments_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(assignments_table)
            
            # Unassigned students section
            if summary.unassigned_students:
                story.append(Spacer(1, 30))
                story.append(Paragraph("Unassigned Students", styles['Heading2']))
                unassigned_text = f"Roll Numbers: {', '.join(map(str, summary.unassigned_students))}"
                story.append(Paragraph(unassigned_text, styles['Normal']))
            
            doc.build(story)
            
            self.logger.info(f"Assignment summary exported to PDF: {base_path}")
            return base_path
            
        except Exception as e:
            self.logger.error(f"Error exporting to PDF: {str(e)}")
            raise
    
    def export_detailed_assignments(self, students: List[Student], mentors: List[Mentor], 
                                  summary: AssignmentSummary, format_type: str = 'csv') -> str:
        """Export detailed assignment information including student and mentor details."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detailed_assignments_{timestamp}"
        
        if format_type == 'csv':
            return self._export_detailed_csv(students, mentors, summary, filename)
        elif format_type == 'excel':
            return self._export_detailed_excel(students, mentors, summary, filename)
        else:
            raise ValueError(f"Format {format_type} not supported for detailed export")
    
    def _export_detailed_csv(self, students: List[Student], mentors: List[Mentor], 
                           summary: AssignmentSummary, filename: str) -> str:
        """Export detailed assignment information to CSV."""
        base_path = os.path.join(config.REPORTS_DIR, f"{filename}.csv")
        
        try:
            with open(base_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Detailed Assignment Report'])
                writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                # Write student-mentor mapping
                writer.writerow(['Student-Mentor Assignments'])
                writer.writerow(['Roll No', 'Student Name', 'Branch', 'Year', 'Mentor ID', 'Mentor Name', 'Department'])
                
                for student in sorted(students, key=lambda s: s.roll_no):
                    mentor_info = None
                    if student.assigned_mentor_id:
                        mentor_info = next((m for m in mentors if m.faculty_id == student.assigned_mentor_id), None)
                    
                    writer.writerow([
                        student.roll_no,
                        student.name,
                        student.branch,
                        student.year,
                        student.assigned_mentor_id or 'Unassigned',
                        mentor_info.name if mentor_info else 'N/A',
                        mentor_info.department if mentor_info else 'N/A'
                    ])
            
            self.logger.info(f"Detailed assignments exported to CSV: {base_path}")
            return base_path
            
        except Exception as e:
            self.logger.error(f"Error exporting detailed CSV: {str(e)}")
            raise
    
    def _export_detailed_excel(self, students: List[Student], mentors: List[Mentor], 
                             summary: AssignmentSummary, filename: str) -> str:
        """Export detailed assignment information to Excel."""
        if not PANDAS_AVAILABLE:
            return self._export_detailed_csv(students, mentors, summary, filename)
        
        base_path = os.path.join(config.REPORTS_DIR, f"{filename}.xlsx")
        
        try:
            with pd.ExcelWriter(base_path, engine='openpyxl') as writer:
                # Student details sheet
                student_data = []
                for student in sorted(students, key=lambda s: s.roll_no):
                    mentor_info = None
                    if student.assigned_mentor_id:
                        mentor_info = next((m for m in mentors if m.faculty_id == student.assigned_mentor_id), None)
                    
                    student_data.append({
                        'Roll No': student.roll_no,
                        'Student Name': student.name,
                        'Branch': student.branch,
                        'Year': student.year,
                        'Email': student.email or 'N/A',
                        'Phone': student.phone or 'N/A',
                        'Mentor ID': student.assigned_mentor_id or 'Unassigned',
                        'Mentor Name': mentor_info.name if mentor_info else 'N/A',
                        'Department': mentor_info.department if mentor_info else 'N/A'
                    })
                
                students_df = pd.DataFrame(student_data)
                students_df.to_excel(writer, sheet_name='Students', index=False)
                
                # Mentor details sheet
                mentor_data = []
                for mentor in mentors:
                    mentor_data.append({
                        'Faculty ID': mentor.faculty_id,
                        'Name': mentor.name,
                        'Department': mentor.department,
                        'Email': mentor.email or 'N/A',
                        'Phone': mentor.phone or 'N/A',
                        'Available': mentor.availability,
                        'Max Students': mentor.max_students,
                        'Assigned Students': mentor.get_student_count(),
                        'Available Slots': mentor.get_available_slots()
                    })
                
                mentors_df = pd.DataFrame(mentor_data)
                mentors_df.to_excel(writer, sheet_name='Mentors', index=False)
            
            self.logger.info(f"Detailed assignments exported to Excel: {base_path}")
            return base_path
            
        except Exception as e:
            self.logger.error(f"Error exporting detailed Excel: {str(e)}")
            raise
    
    def export_to_json(self, summary: AssignmentSummary, filename: Optional[str] = None) -> str:
        """Export assignment summary to JSON format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if filename is None:
            filename = f"assignment_summary_{timestamp}"
        
        base_path = os.path.join(config.REPORTS_DIR, f"{filename}.json")
        
        try:
            with open(base_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(summary.to_dict(), jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Assignment summary exported to JSON: {base_path}")
            return base_path
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            raise
