# 🎓 Student-Mentor Assignment System - Streamlit Dashboard

A modern web-based dashboard for automating student-mentor assignments with intelligent remainder handling.

## 🚀 Quick Start

### Option 1: Direct Run
```bash
python start_dashboard.py
```

### Option 2: Manual Run
```bash
streamlit run streamlit_dashboard.py
```

### Option 3: With Virtual Environment
```bash
.venv/Scripts/python.exe -m streamlit run streamlit_dashboard.py
```

## 🌐 Access Dashboard

Once started, the dashboard will be available at:
- **Local URL:** http://localhost:8501
- **Network URL:** http://[your-ip]:8501

## 📱 Dashboard Features

### 🏠 Dashboard Page
- **Real-time Statistics** - View student/mentor counts and assignment status
- **Interactive Charts** - Assignment distribution and mentor utilization
- **Current Assignments** - See all mentor-student assignments
- **Configuration Display** - View current system settings

### 👥 Students Page  
- **Student List** - View all students with filtering options
- **Filter by Branch/Year/Status** - Easy data filtering
- **Statistics** - Student counts and distribution charts

### 👨‍🏫 Mentors Page
- **Mentor List** - View all mentors with capacity information
- **Utilization Tracking** - See mentor workload and availability
- **Department Analysis** - Mentor distribution by department

### ⚙️ Assignment Page
- **Quick Actions** - Create sample data, run assignments, quick tests
- **Assignment Preview** - See how students will be distributed
- **Configuration Details** - View assignment rules and examples

### 📊 Analytics Page
- **Assignment Insights** - Assignment rates and capacity utilization
- **Distribution Charts** - Student/mentor analysis
- **Workload Analysis** - Mentor performance metrics

### 📥 Export Page
- **Multiple Formats** - Export to CSV, Excel, PDF, JSON
- **Data Preview** - See assignment data before export
- **Download Options** - Direct file downloads

## 🔧 Core Features

### ✅ Assignment Algorithm
- **30 students per mentor** - Automated batch assignment
- **Smart remainder handling** - Configurable threshold (≤12 to last mentor, >12 new mentor)
- **Roll number sorting** - Automatic student ordering

### ✅ Data Management
- **CSV storage** - Simple, portable data format
- **Sample data generation** - Quick testing capabilities
- **Validation** - Data integrity checks

### ✅ Export Capabilities
- **CSV Export** - Standard spreadsheet format
- **Excel Export** - Advanced spreadsheet with formatting
- **PDF Export** - Professional report format
- **JSON Export** - Data interchange format

## ⚙️ Configuration

Current settings (in `src/utils/config.py`):
- **Batch Size:** 30 students per mentor
- **Remainder Threshold:** 12 students
- **Sort by Roll Number:** True
- **Allow Mentor Overload:** True

## 📂 Project Structure

```
c:\Projects\Automation-model-mentor\
├── streamlit_dashboard.py      # Main Streamlit application
├── start_dashboard.py          # Easy start script
├── src/
│   ├── models/                 # Data models (Student, Mentor, Assignment)
│   ├── services/               # Business logic (Assignment, Data, Export)
│   └── utils/                  # Configuration and utilities
├── data/                       # CSV data storage
├── reports/                    # Export outputs
└── .venv/                      # Python virtual environment
```

## 🎯 Assignment Logic Examples

- **65 students:** 30 + 35 (5 added to last mentor)
- **72 students:** 30 + 42 (12 added to last mentor)
- **73 students:** 30 + 30 + 13 (13 gets new mentor)
- **100 students:** 30 + 30 + 30 + 10 (10 added to last mentor)

## 🔄 Technology Stack

- **Frontend:** Streamlit (Modern Python web framework)
- **Backend:** Python 3.11 with object-oriented design
- **Visualization:** Plotly charts for interactive data analysis
- **Data:** Pandas for data manipulation and CSV storage
- **Export:** Multiple format support (openpyxl, reportlab)

## 🆚 Streamlit vs Flask

**Previous Flask Setup:**
- ❌ Complex HTML/CSS/JavaScript templates
- ❌ Manual route handling and form processing
- ❌ Separate frontend/backend coordination
- ❌ Bootstrap styling maintenance

**New Streamlit Setup:**
- ✅ Pure Python with automatic UI generation
- ✅ Built-in interactive widgets and charts
- ✅ Automatic reactivity and state management
- ✅ Modern, responsive design out-of-the-box
- ✅ Faster development and easier maintenance

## 🛠️ Development Commands

```bash
# Install dependencies
pip install streamlit plotly pandas

# Run dashboard
streamlit run streamlit_dashboard.py

# Create sample data (from dashboard)
# Click "Create Sample Data" button

# Run assignment (from dashboard)  
# Click "Run Assignment" button

# Quick test (from dashboard)
# Click "Quick Test (73 Students)" button
```

## 📋 Next Steps

1. **🌐 Access Dashboard:** Open http://localhost:8501
2. **📊 Create Sample Data:** Use the sidebar quick action
3. **🎯 Run Assignment:** Test the algorithm
4. **📥 Export Results:** Download reports in your preferred format
5. **📈 Analyze Data:** Use the Analytics page for insights

---

**🎉 Your modern Student-Mentor Assignment Dashboard is ready!**
