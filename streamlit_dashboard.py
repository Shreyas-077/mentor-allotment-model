"""
Modern Streamlit Dashboard for Student-Mentor Assignment System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import json
import io

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.data_service import DataService
from services.assignment_service import AssignmentService
from services.export_service import ExportService
from models.student import Student
from models.mentor import Mentor
from models.assignment import Assignment, AssignmentSummary
from utils.config import config

# Initialize services
@st.cache_resource
def get_services():
    return DataService(), AssignmentService(), ExportService()

data_service, assignment_service, export_service = get_services()

# Page config
st.set_page_config(
    page_title="Student-Mentor Assignment System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4a69bd 0%, #5f3dc4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4a69bd;
    }
    .success-box {
        background: #f8fff9;
        color: #2d5a2d;
        border: 2px solid #28a745;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin: 1rem 0;
        font-weight: 500;
    }
    .warning-box {
        background: #fffef7;
        color: #856404;
        border: 2px solid #ffc107;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin: 1rem 0;
        font-weight: 500;
    }
    .info-box {
        background: #f0f8ff;
        color: #0c4085;
        border: 2px solid #17a2b8;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin: 1rem 0;
        font-weight: 500;
    }
    .stDataFrame {
        background: white;
    }
    .stDataFrame table {
        color: #333 !important;
    }
    .stDataFrame th {
        background-color: #f8f9fa !important;
        color: #495057 !important;
        font-weight: 600 !important;
    }
    .stDataFrame td {
        color: #212529 !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Student-Mentor Assignment System</h1>
        <p>Intelligent automation for student-mentor assignments with remainder handling</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Menu")
        page = st.selectbox(
            "Choose a page:",
            ["🏠 Dashboard", "👥 Students", "👨‍🏫 Mentors", "⚙️ Assignment", "📊 Analytics", "📥 Export"]
        )
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        if st.button("🎯 Run Assignment", use_container_width=True):
            run_assignment()
        
        # Configuration display
        st.markdown("---")
        st.subheader("⚙️ Configuration")
        st.write(f"**Batch Size:** {config.BATCH_SIZE}")
        st.write(f"**Remainder Threshold:** {config.ASSIGNMENT_RULES['remainder_threshold']}")
        
    # Route to different pages
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Students":
        show_students()
    elif page == "👨‍🏫 Mentors":
        show_mentors()
    elif page == "⚙️ Assignment":
        show_assignment()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "📥 Export":
        show_export()

def show_dashboard():
    """Main dashboard view"""
    st.header("📊 Dashboard Overview")
    
    # Load data
    students = data_service.load_students()
    mentors = data_service.load_mentors()
    summary = data_service.get_data_summary()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Students",
            value=summary.get('total_students', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="👨‍🏫 Total Mentors",
            value=summary.get('total_mentors', 0),
            delta=None
        )
    
    assigned_count = len([s for s in students if s.assigned_mentor_id])
    unassigned_count = len([s for s in students if not s.assigned_mentor_id])
    
    with col3:
        st.metric(
            label="✅ Assigned Students",
            value=assigned_count,
            delta=None
        )
    
    with col4:
        st.metric(
            label="⏳ Unassigned Students",
            value=unassigned_count,
            delta=None
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Assignment distribution pie chart
        if students:
            fig = px.pie(
                values=[assigned_count, unassigned_count],
                names=['Assigned', 'Unassigned'],
                title="📊 Assignment Distribution",
                color_discrete_map={'Assigned': '#28a745', 'Unassigned': '#ffc107'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📝 No student data available. Please add student and mentor data to get started!")
    
    with col2:
        # Mentor utilization
        if mentors and students:
            mentor_data = []
            for mentor in mentors:
                assigned_students = [s for s in students if s.assigned_mentor_id == mentor.faculty_id]
                utilization = (len(assigned_students) / mentor.max_students * 100) if mentor.max_students > 0 else 0
                mentor_data.append({
                    'Mentor': mentor.name,
                    'Utilization': utilization,
                    'Students': len(assigned_students),
                    'Capacity': mentor.max_students
                })
            
            if mentor_data:
                df = pd.DataFrame(mentor_data)
                fig = px.bar(
                    df, 
                    x='Mentor', 
                    y='Utilization',
                    title="📈 Mentor Utilization (%)",
                    color='Utilization',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No mentor utilization data available.")
    
    # Current assignments
    if students and mentors:
        show_current_assignments(students, mentors)
    
    # Configuration info
    st.markdown("---")
    st.subheader("⚙️ Current Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <strong>📋 Assignment Rules:</strong><br>
            • Batch Size: {config.BATCH_SIZE} students per mentor<br>
            • Remainder Threshold: {config.ASSIGNMENT_RULES['remainder_threshold']} students<br>
            • Sort by Roll Number: {config.ASSIGNMENT_RULES['sort_by_roll_number']}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <strong>🔧 Logic:</strong><br>
            • If remainder ≤ {config.ASSIGNMENT_RULES['remainder_threshold']}: Add to last mentor<br>
            • If remainder > {config.ASSIGNMENT_RULES['remainder_threshold']}: Create new mentor<br>
            • Allow Overload: {config.ASSIGNMENT_RULES['allow_mentor_overload']}
        </div>
        """, unsafe_allow_html=True)

def show_current_assignments(students, mentors):
    """Show current assignment overview"""
    st.markdown("---")
    st.subheader("📋 Current Assignments")
    
    # Create assignment data
    assignment_data = []
    for mentor in mentors:
        assigned_students = [s for s in students if s.assigned_mentor_id == mentor.faculty_id]
        if assigned_students:
            utilization = (len(assigned_students) / mentor.max_students * 100) if mentor.max_students > 0 else 0
            assignment_data.append({
                'Mentor ID': mentor.faculty_id,
                'Mentor Name': mentor.name,
                'Department': mentor.department,
                'Assigned Students': len(assigned_students),
                'Max Capacity': mentor.max_students,
                'Utilization (%)': round(utilization, 1)
            })
    
    if assignment_data:
        df = pd.DataFrame(assignment_data)
        
        # Color code based on utilization with better contrast
        def color_utilization(val):
            if val <= 100:
                return 'background-color: #e8f5e8; color: #2e7a2e'  # Light green with dark green text
            elif val <= 120:
                return 'background-color: #fff8e1; color: #8a6914'  # Light yellow with dark yellow text
            else:
                return 'background-color: #ffeaea; color: #c53030'  # Light red with dark red text
        
        styled_df = df.style.map(color_utilization, subset=['Utilization (%)'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Show some statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_utilization = df['Utilization (%)'].mean()
            st.metric("📊 Average Utilization", f"{avg_utilization:.1f}%")
        
        with col2:
            overloaded = len(df[df['Utilization (%)'] > 100])
            st.metric("⚠️ Overloaded Mentors", overloaded)
        
        with col3:
            total_capacity = df['Max Capacity'].sum()
            total_assigned = df['Assigned Students'].sum()
            st.metric("📈 System Utilization", f"{(total_assigned/total_capacity*100):.1f}%")
    else:
        st.info("📝 No assignments found. Run assignment to see results here.")

def show_students():
    """Students management page"""
    st.header("👥 Students Management")
    
    # Add new student section
    st.subheader("➕ Add New Student")
    
    # Toggle between manual and CSV upload
    add_method = st.radio("Choose method:", ["📝 Manual Entry", "📁 CSV Upload"], horizontal=True)
    
    if add_method == "📝 Manual Entry":
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                roll_no = st.number_input("Roll Number", min_value=1, step=1)
                name = st.text_input("Student Name")
                branch = st.selectbox("Branch", ["CSE", "ECE", "ME", "CE", "IT", "EEE", "Other"])
            
            with col2:
                year = st.selectbox("Year", [1, 2, 3, 4])
                email = st.text_input("Email (optional)")
                phone = st.text_input("Phone (optional)")
            
            submitted = st.form_submit_button("✅ Add Student")
            
            if submitted:
                if roll_no and name:
                    try:
                        # Check if roll number already exists
                        existing_students = data_service.load_students()
                        if any(s.roll_no == roll_no for s in existing_students):
                            st.error(f"❌ Student with roll number {roll_no} already exists!")
                        else:
                            new_student = Student(
                                roll_no=roll_no,
                                name=name,
                                branch=branch,
                                year=year,
                                email=email if email else None,
                                phone=phone if phone else None
                            )
                            
                            # Add to existing students
                            existing_students.append(new_student)
                            data_service.save_students(existing_students)
                            
                            st.success(f"✅ Student {name} (Roll: {roll_no}) added successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding student: {str(e)}")
                else:
                    st.error("❌ Please fill in Roll Number and Name")
    
    else:  # CSV Upload
        st.write("Upload a CSV file with columns: roll_no, name, branch, year, email, phone")
        
        # Download template
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Download CSV Template", key="student_template"):
                template_data = {
                    'roll_no': [2023001, 2023002, 2023003],
                    'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
                    'branch': ['CSE', 'ECE', 'ME'],
                    'year': [3, 2, 1],
                    'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
                    'phone': ['1234567890', '0987654321', '1122334455']
                }
                template_df = pd.DataFrame(template_data)
                csv_data = template_df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download Template",
                    data=csv_data,
                    file_name="students_template.csv",
                    mime="text/csv"
                )
        
        # Show sample format
        with st.expander("📋 View CSV Format Example"):
            sample_data = {
                'roll_no': [2023001, 2023002, 2023003],
                'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
                'branch': ['CSE', 'ECE', 'ME'],
                'year': [3, 2, 1],
                'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
                'phone': ['1234567890', '0987654321', '1122334455']
            }
            st.dataframe(pd.DataFrame(sample_data))
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['roll_no', 'name', 'branch', 'year']
                if all(col in df.columns for col in required_columns):
                    
                    # Preview data
                    st.write("📋 Preview of uploaded data:")
                    st.dataframe(df.head())
                    
                    if st.button("✅ Import Students"):
                        existing_students = data_service.load_students()
                        existing_roll_nos = {s.roll_no for s in existing_students}
                        
                        new_students = []
                        skipped = 0
                        
                        for _, row in df.iterrows():
                            if row['roll_no'] not in existing_roll_nos:
                                student = Student(
                                    roll_no=int(row['roll_no']),
                                    name=str(row['name']),
                                    branch=str(row['branch']),
                                    year=int(row['year']),
                                    email=str(row.get('email', '')) if pd.notna(row.get('email')) else None,
                                    phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None
                                )
                                new_students.append(student)
                                existing_students.append(student)
                            else:
                                skipped += 1
                        
                        if new_students:
                            data_service.save_students(existing_students)
                            st.success(f"✅ Imported {len(new_students)} students! (Skipped {skipped} duplicates)")
                            st.rerun()
                        else:
                            st.warning("⚠️ No new students to import (all roll numbers already exist)")
                
                else:
                    st.error(f"❌ CSV must contain columns: {', '.join(required_columns)}")
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV file: {str(e)}")
    
    st.markdown("---")
    
    students = data_service.load_students()
    
    if students:
        # Convert to DataFrame for better display
        student_data = []
        for student in students:
            student_data.append({
                'Roll No': student.roll_no,
                'Name': student.name,
                'Branch': student.branch,
                'Year': student.year,
                'Email': student.email or 'N/A',
                'Assigned Mentor': student.assigned_mentor_id or 'Unassigned',
                'Status': '✅ Assigned' if student.assigned_mentor_id else '⏳ Unassigned'
            })
        
        df = pd.DataFrame(student_data)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            branch_filter = st.selectbox("Filter by Branch:", ['All'] + list(df['Branch'].unique()))
        
        with col2:
            year_filter = st.selectbox("Filter by Year:", ['All'] + list(df['Year'].unique()))
        
        with col3:
            status_filter = st.selectbox("Filter by Status:", ['All', '✅ Assigned', '⏳ Unassigned'])
        
        # Apply filters
        filtered_df = df.copy()
        if branch_filter != 'All':
            filtered_df = filtered_df[filtered_df['Branch'] == branch_filter]
        if year_filter != 'All':
            filtered_df = filtered_df[filtered_df['Year'] == year_filter]
        if status_filter != 'All':
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Students", len(df))
        with col2:
            st.metric("✅ Assigned", len(df[df['Status'] == '✅ Assigned']))
        with col3:
            st.metric("⏳ Unassigned", len(df[df['Status'] == '⏳ Unassigned']))
        with col4:
            st.metric("🔍 Filtered", len(filtered_df))
        
        # Display table
        st.dataframe(filtered_df, use_container_width=True)
        
        # Management actions
        st.subheader("🔧 Management Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Students", type="secondary"):
                if st.session_state.get('confirm_clear_students', False):
                    data_service.save_students([])  # Save empty list
                    st.success("✅ All students cleared!")
                    st.session_state.confirm_clear_students = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_students = True
                    st.warning("⚠️ Click again to confirm clearing all students")
        
        with col2:
            # Reset confirmation if user does something else
            if 'confirm_clear_students' in st.session_state and st.session_state.confirm_clear_students:
                if st.button("❌ Cancel Clear"):
                    st.session_state.confirm_clear_students = False
                    st.rerun()
        
        # Branch distribution chart
        if len(df) > 0:
            branch_counts = df['Branch'].value_counts()
            fig = px.bar(
                x=branch_counts.index,
                y=branch_counts.values,
                title="📊 Students by Branch",
                labels={'x': 'Branch', 'y': 'Number of Students'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 No student data found. Please add student data to get started!")

def show_mentors():
    """Mentors management page"""
    st.header("👨‍🏫 Mentors Management")
    
    # Add new mentor section
    st.subheader("➕ Add New Mentor")
    
    # Toggle between manual and CSV upload
    add_method = st.radio("Choose method:", ["📝 Manual Entry", "📁 CSV Upload"], horizontal=True, key="mentor_method")
    
    if add_method == "📝 Manual Entry":
        with st.form("add_mentor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                faculty_id = st.text_input("Faculty ID")
                name = st.text_input("Mentor Name")
                department = st.selectbox("Department", ["CSE", "ECE", "ME", "CE", "IT", "EEE", "Mathematics", "Physics", "Chemistry", "Other"])
            
            with col2:
                max_students = st.number_input("Max Students", min_value=1, value=30, step=1)
                email = st.text_input("Email (optional)")
                phone = st.text_input("Phone (optional)")
            
            availability = st.checkbox("Available for assignment", value=True)
            
            submitted = st.form_submit_button("✅ Add Mentor")
            
            if submitted:
                if faculty_id and name:
                    try:
                        # Check if faculty ID already exists
                        existing_mentors = data_service.load_mentors()
                        if any(m.faculty_id == faculty_id for m in existing_mentors):
                            st.error(f"❌ Mentor with Faculty ID {faculty_id} already exists!")
                        else:
                            new_mentor = Mentor(
                                faculty_id=faculty_id,
                                name=name,
                                department=department,
                                max_students=max_students,
                                availability=availability,
                                email=email if email else None,
                                phone=phone if phone else None
                            )
                            
                            # Add to existing mentors
                            existing_mentors.append(new_mentor)
                            data_service.save_mentors(existing_mentors)
                            
                            st.success(f"✅ Mentor {name} (ID: {faculty_id}) added successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding mentor: {str(e)}")
                else:
                    st.error("❌ Please fill in Faculty ID and Name")
    
    else:  # CSV Upload
        st.write("Upload a CSV file with columns: faculty_id, name, department, max_students, availability, email, phone")
        
        # Download template
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Download CSV Template", key="mentor_template"):
                template_data = {
                    'faculty_id': ['MENT001', 'MENT002', 'MENT003'],
                    'name': ['Dr. Smith', 'Prof. Johnson', 'Dr. Brown'],
                    'department': ['CSE', 'ECE', 'ME'],
                    'max_students': [30, 25, 35],
                    'availability': [True, True, False],
                    'email': ['smith@university.edu', 'johnson@university.edu', 'brown@university.edu'],
                    'phone': ['1234567890', '0987654321', '1122334455']
                }
                template_df = pd.DataFrame(template_data)
                csv_data = template_df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download Template",
                    data=csv_data,
                    file_name="mentors_template.csv",
                    mime="text/csv"
                )
        
        # Show sample format
        with st.expander("📋 View CSV Format Example"):
            sample_data = {
                'faculty_id': ['MENT001', 'MENT002', 'MENT003'],
                'name': ['Dr. Smith', 'Prof. Johnson', 'Dr. Brown'],
                'department': ['CSE', 'ECE', 'ME'],
                'max_students': [30, 25, 35],
                'availability': [True, True, False],
                'email': ['smith@university.edu', 'johnson@university.edu', 'brown@university.edu'],
                'phone': ['1234567890', '0987654321', '1122334455']
            }
            st.dataframe(pd.DataFrame(sample_data))
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="mentor_csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['faculty_id', 'name', 'department', 'max_students']
                if all(col in df.columns for col in required_columns):
                    
                    # Preview data
                    st.write("📋 Preview of uploaded data:")
                    st.dataframe(df.head())
                    
                    if st.button("✅ Import Mentors"):
                        existing_mentors = data_service.load_mentors()
                        existing_faculty_ids = {m.faculty_id for m in existing_mentors}
                        
                        new_mentors = []
                        skipped = 0
                        
                        for _, row in df.iterrows():
                            if row['faculty_id'] not in existing_faculty_ids:
                                mentor = Mentor(
                                    faculty_id=str(row['faculty_id']),
                                    name=str(row['name']),
                                    department=str(row['department']),
                                    max_students=int(row['max_students']),
                                    availability=bool(row.get('availability', True)),
                                    email=str(row.get('email', '')) if pd.notna(row.get('email')) else None,
                                    phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None
                                )
                                new_mentors.append(mentor)
                                existing_mentors.append(mentor)
                            else:
                                skipped += 1
                        
                        if new_mentors:
                            data_service.save_mentors(existing_mentors)
                            st.success(f"✅ Imported {len(new_mentors)} mentors! (Skipped {skipped} duplicates)")
                            st.rerun()
                        else:
                            st.warning("⚠️ No new mentors to import (all faculty IDs already exist)")
                
                else:
                    st.error(f"❌ CSV must contain columns: {', '.join(required_columns)}")
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV file: {str(e)}")
    
    st.markdown("---")
    
    mentors = data_service.load_mentors()
    students = data_service.load_students()
    
    if mentors:
        # Convert to DataFrame for better display
        mentor_data = []
        for mentor in mentors:
            assigned_students = [s for s in students if s.assigned_mentor_id == mentor.faculty_id]
            mentor_data.append({
                'Faculty ID': mentor.faculty_id,
                'Name': mentor.name,
                'Department': mentor.department,
                'Email': mentor.email or 'N/A',
                'Max Students': mentor.max_students,
                'Assigned Students': len(assigned_students),
                'Utilization (%)': round((len(assigned_students) / mentor.max_students * 100), 1) if mentor.max_students > 0 else 0,
                'Status': '✅ Available' if mentor.availability else '❌ Unavailable'
            })
        
        df = pd.DataFrame(mentor_data)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            dept_filter = st.selectbox("Filter by Department:", ['All'] + list(df['Department'].unique()))
        
        with col2:
            status_filter = st.selectbox("Filter by Status:", ['All', '✅ Available', '❌ Unavailable'])
        
        # Apply filters
        filtered_df = df.copy()
        if dept_filter != 'All':
            filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
        if status_filter != 'All':
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Mentors", len(df))
        with col2:
            st.metric("✅ Available", len(df[df['Status'] == '✅ Available']))
        with col3:
            st.metric("👥 Total Capacity", df['Max Students'].sum())
        with col4:
            st.metric("📈 Avg Utilization", f"{df['Utilization (%)'].mean():.1f}%")
        
        # Color code the dataframe
        def color_utilization(val):
            if val <= 100:
                return 'background-color: #d4edda'  # Green
            elif val <= 120:
                return 'background-color: #fff3cd'  # Yellow
            else:
                return 'background-color: #f8d7da'  # Red
        
        styled_df = filtered_df.style.map(color_utilization, subset=['Utilization (%)'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Management actions
        st.subheader("🔧 Management Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Mentors", type="secondary"):
                if st.session_state.get('confirm_clear_mentors', False):
                    data_service.save_mentors([])  # Save empty list
                    st.success("✅ All mentors cleared!")
                    st.session_state.confirm_clear_mentors = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_mentors = True
                    st.warning("⚠️ Click again to confirm clearing all mentors")
        
        with col2:
            # Reset confirmation if user does something else
            if 'confirm_clear_mentors' in st.session_state and st.session_state.confirm_clear_mentors:
                if st.button("❌ Cancel Clear"):
                    st.session_state.confirm_clear_mentors = False
                    st.rerun()
        
        # Department distribution chart
        if len(df) > 0:
            dept_counts = df['Department'].value_counts()
            fig = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="📊 Mentors by Department"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 No mentor data found. Please add mentor data to get started!")

def show_assignment():
    """Assignment operations page"""
    st.header("⚙️ Assignment Operations")
    
    # Load current data
    students = data_service.load_students()
    mentors = data_service.load_mentors()
    
    # Data status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Status")
        if students and mentors:
            st.success(f"✅ Ready! {len(students)} students, {len(mentors)} mentors")
        else:
            st.warning("⚠️ Missing data. Please add student and mentor data first.")
    
    with col2:
        st.subheader("🎯 Assignment Preview")
        if students:
            batches = len(students) // config.BATCH_SIZE
            remainder = len(students) % config.BATCH_SIZE
            
            if remainder <= config.ASSIGNMENT_RULES['remainder_threshold']:
                st.info(f"📋 Will create {batches} batches + {remainder} students to last mentor")
            else:
                st.info(f"📋 Will create {batches + 1} batches (remainder gets new mentor)")
    
    st.markdown("---")
    
    # Action button
    if st.button("🎯 Run Assignment", use_container_width=True, type="primary"):
        run_assignment()
    
    # Configuration section
    st.markdown("---")
    st.subheader("⚙️ Configuration Details")
    
    config_col1, config_col2 = st.columns(2)
    
    with config_col1:
        st.markdown(f"""
        **📋 Assignment Rules:**
        - **Batch Size:** {config.BATCH_SIZE} students per mentor
        - **Remainder Threshold:** {config.ASSIGNMENT_RULES['remainder_threshold']} students
        - **Sort by Roll Number:** {config.ASSIGNMENT_RULES['sort_by_roll_number']}
        - **Allow Mentor Overload:** {config.ASSIGNMENT_RULES['allow_mentor_overload']}
        """)
    
    with config_col2:
        st.markdown(f"""
        **🔧 Assignment Examples:**
        - **65 students:** 30 + 35 (5 added to last mentor)
        - **72 students:** 30 + 42 (12 added to last mentor)
        - **73 students:** 30 + 30 + 13 (13 gets new mentor)
        - **100 students:** 30 + 30 + 30 + 10 (10 added to last mentor)
        """)

def show_analytics():
    """Analytics and insights page"""
    st.header("📊 Analytics & Insights")
    
    students = data_service.load_students()
    mentors = data_service.load_mentors()
    
    if not students or not mentors:
        st.warning("⚠️ No data available for analytics. Please add student and mentor data first.")
        return
    
    # Key insights
    assigned_students = [s for s in students if s.assigned_mentor_id]
    unassigned_students = [s for s in students if not s.assigned_mentor_id]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assignment_rate = (len(assigned_students) / len(students) * 100) if students else 0
        st.metric("📈 Assignment Rate", f"{assignment_rate:.1f}%")
    
    with col2:
        avg_mentor_load = len(assigned_students) / len(mentors) if mentors else 0
        st.metric("👥 Avg Students/Mentor", f"{avg_mentor_load:.1f}")
    
    with col3:
        total_capacity = sum(m.max_students for m in mentors)
        capacity_utilization = (len(assigned_students) / total_capacity * 100) if total_capacity else 0
        st.metric("🏢 Capacity Utilization", f"{capacity_utilization:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Branch distribution
        if students:
            branch_data = pd.DataFrame([{'Branch': s.branch, 'Year': s.year} for s in students])
            branch_counts = branch_data['Branch'].value_counts()
            
            fig = px.bar(
                x=branch_counts.index,
                y=branch_counts.values,
                title="📊 Students by Branch",
                labels={'x': 'Branch', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Year distribution
        if students:
            year_counts = branch_data['Year'].value_counts().sort_index()
            
            fig = px.pie(
                values=year_counts.values,
                names=year_counts.index,
                title="📊 Students by Year"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Mentor workload analysis
    st.subheader("👨‍🏫 Mentor Workload Analysis")
    
    mentor_analysis = []
    for mentor in mentors:
        assigned = [s for s in students if s.assigned_mentor_id == mentor.faculty_id]
        workload = len(assigned) / mentor.max_students if mentor.max_students > 0 else 0
        
        mentor_analysis.append({
            'Mentor': mentor.name,
            'Department': mentor.department,
            'Assigned': len(assigned),
            'Capacity': mentor.max_students,
            'Workload': workload,
            'Status': 'Overloaded' if workload > 1.0 else 'Normal'
        })
    
    df = pd.DataFrame(mentor_analysis)
    
    if len(df) > 0:
        # Workload distribution chart
        fig = px.histogram(
            df,
            x='Workload',
            nbins=20,
            title="📊 Mentor Workload Distribution",
            labels={'Workload': 'Workload Ratio', 'count': 'Number of Mentors'}
        )
        fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="100% Capacity")
        st.plotly_chart(fig, use_container_width=True)
        
        # Department workload comparison
        dept_workload = df.groupby('Department')['Workload'].mean().reset_index()
        fig = px.bar(
            dept_workload,
            x='Department',
            y='Workload',
            title="📊 Average Workload by Department"
        )
        fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="100% Capacity")
        st.plotly_chart(fig, use_container_width=True)

def show_export():
    """Export data page"""
    st.header("📥 Export Data")
    
    students = data_service.load_students()
    mentors = data_service.load_mentors()
    
    if not students:
        st.warning("⚠️ No student data to export. Please add student and mentor data first.")
        return
    
    # Create assignment summary from current data
    # Group students by assigned mentor
    assignments = []
    batch_number = 1
    assigned_students = [s for s in students if s.assigned_mentor_id]
    unassigned_students = [s for s in students if not s.assigned_mentor_id]
    
    # Create assignments for each mentor with students
    mentor_student_map = {}
    for student in assigned_students:
        if student.assigned_mentor_id not in mentor_student_map:
            mentor_student_map[student.assigned_mentor_id] = []
        mentor_student_map[student.assigned_mentor_id].append(student.roll_no)
    
    for mentor_id, student_rolls in mentor_student_map.items():
        assignment = Assignment(
            mentor_id=mentor_id,
            student_roll_numbers=student_rolls,
            assignment_date=datetime.now(),
            batch_number=batch_number
        )
        assignments.append(assignment)
        batch_number += 1
    
    # Create summary
    summary = AssignmentSummary(
        total_students=len(students),
        total_mentors=len(mentors),
        total_assignments=len(assignments),
        students_per_mentor_avg=len(assigned_students) / len(assignments) if assignments else 0,
        unassigned_students=[s.roll_no for s in unassigned_students],
        assignments=assignments,
        created_date=datetime.now()
    )
    
    st.subheader("📋 Assignment Summary Export")
    st.write("Export summary of assignments and statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Export as CSV", use_container_width=True):
            export_data('csv', summary)
    
    with col2:
        if st.button("📊 Export as Excel", use_container_width=True):
            export_data('excel', summary)
    
    with col3:
        if st.button("📑 Export as PDF", use_container_width=True):
            export_data('pdf', summary)
    
    with col4:
        if st.button("🔗 Export as JSON", use_container_width=True):
            export_data('json', summary)
    
    # Detailed mentor-student export section
    st.markdown("---")
    st.subheader("👥 Detailed Mentor-Student Export")
    st.write("Export complete list of mentors with their assigned students")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download Mentor-Student CSV", use_container_width=True):
            export_detailed_data('csv', students, mentors, summary)
    
    with col2:
        if st.button("📊 Download Mentor-Student Excel", use_container_width=True):
            export_detailed_data('excel', students, mentors, summary)
    
    # Preview data
    st.markdown("---")
    st.subheader("👀 Data Preview")
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Assignments", summary.total_assignments)
    
    with col2:
        # Calculate students assigned from the summary
        students_assigned = summary.total_students - len(summary.unassigned_students)
        st.metric("👥 Students Assigned", students_assigned)
    
    with col3:
        # Count unique mentors from assignments
        mentors_used = len(set(assignment.mentor_id for assignment in summary.assignments))
        st.metric("👨‍🏫 Mentors Used", mentors_used)
    
    # Detailed mentor-student preview
    st.subheader("👥 Mentor-Student Assignment Preview")
    
    # Create detailed preview data
    mentor_student_data = []
    for mentor in mentors:
        mentor_students = [s for s in students if s.assigned_mentor_id == mentor.faculty_id]
        
        if mentor_students:
            # For each student under this mentor
            for student in mentor_students:
                mentor_student_data.append({
                    'Mentor ID': mentor.faculty_id,
                    'Mentor Name': mentor.name,
                    'Department': mentor.department,
                    'Student Roll No': str(student.roll_no),  # Convert to string
                    'Student Name': student.name,
                    'Branch': student.branch,
                    'Year': str(student.year)  # Convert to string
                })
        else:
            # Show mentor with no students
            mentor_student_data.append({
                'Mentor ID': mentor.faculty_id,
                'Mentor Name': mentor.name,
                'Department': mentor.department,
                'Student Roll No': 'No students assigned',
                'Student Name': '-',
                'Branch': '-',
                'Year': '-'
            })
    
    if mentor_student_data:
        df_mentor_student = pd.DataFrame(mentor_student_data)
        st.dataframe(df_mentor_student, use_container_width=True)
    else:
        st.info("No mentor-student assignments found.")

    # Assignment details table
    st.subheader("📋 Assignment Summary")
    if summary.assignments:
        assignment_data = []
        for assignment in summary.assignments:
            # Take first 5 student roll numbers for display
            student_rolls = assignment.student_roll_numbers[:5]
            roll_display = ', '.join(map(str, student_rolls))
            if len(assignment.student_roll_numbers) > 5:
                roll_display += '...'
                
            assignment_data.append({
                'Mentor ID': assignment.mentor_id,
                'Batch Number': assignment.batch_number,
                'Students Assigned': len(assignment.student_roll_numbers),
                'Student Roll Numbers': roll_display
            })
        
        df = pd.DataFrame(assignment_data)
        st.dataframe(df, use_container_width=True)

# Helper functions
def run_assignment():
    """Run student assignment"""
    try:
        students = data_service.load_students()
        mentors = data_service.load_mentors()
        
        if not students:
            st.error("❌ No students found. Please add student data first.")
            return
        
        if not mentors:
            st.error("❌ No mentors found. Please add mentor data first.")
            return
        
        with st.spinner('Running assignment algorithm...'):
            summary = assignment_service.assign_students_to_mentors(students, mentors)
            
            # Save updated data
            data_service.save_students(students)
            data_service.save_mentors(mentors)
            
            st.success(f"✅ Assignment completed! {summary.total_assignments} batches created.")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error during assignment: {str(e)}")

def export_detailed_data(format_type, students, mentors, summary):
    """Export detailed mentor-student data in specified format"""
    try:
        with st.spinner(f'Exporting detailed data as {format_type.upper()}...'):
            file_path = export_service.export_detailed_assignments(students, mentors, summary, format_type)
            
            # Read file and create download button
            with open(file_path, 'rb') as file:
                file_data = file.read()
                
                st.download_button(
                    label=f"📥 Download Detailed {format_type.upper()} File",
                    data=file_data,
                    file_name=os.path.basename(file_path),
                    mime=get_mime_type(format_type)
                )
            
            st.success(f"✅ Detailed {format_type.upper()} file ready for download!")
            
    except Exception as e:
        st.error(f"❌ Error exporting detailed data: {str(e)}")

def export_data(format_type, summary):
    """Export data in specified format"""
    try:
        with st.spinner(f'Exporting data as {format_type.upper()}...'):
            file_path = export_service.export_assignment_summary(summary, format_type)
            
            # Read file and create download button
            with open(file_path, 'rb') as file:
                file_data = file.read()
                
                st.download_button(
                    label=f"📥 Download {format_type.upper()} File",
                    data=file_data,
                    file_name=os.path.basename(file_path),
                    mime=get_mime_type(format_type)
                )
            
            st.success(f"✅ {format_type.upper()} file ready for download!")
            
    except Exception as e:
        st.error(f"❌ Error exporting data: {str(e)}")

def get_mime_type(format_type):
    """Get MIME type for file format"""
    mime_types = {
        'csv': 'text/csv',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pdf': 'application/pdf',
        'json': 'application/json'
    }
    return mime_types.get(format_type, 'application/octet-stream')

if __name__ == "__main__":
    # Ensure directories exist
    config.ensure_directories_exist()
    main()
