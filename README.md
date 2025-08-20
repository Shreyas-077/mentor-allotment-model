# Student-Mentor Assignment Automation Model

🎓 **A comprehensive system for automatically assigning students to mentors with an interactive Streamlit dashboard**

## 🚀 Features

- **Automated Batch Assignment**: Assigns students to mentors in configurable batch sizes (default: 30 students per mentor)
- **Smart Remainder Handling**: Extra students automatically assigned to the last mentor
- **Interactive Dashboard**: Modern Streamlit web interface with real-time data visualization
- **Multiple Export Formats**: CSV, Excel, PDF, and JSON exports with detailed mentor-student mappings
- **Data Validation**: Comprehensive validation for all input data
- **Sample Data Generator**: Built-in sample data for testing (65 students + 3 mentors)
- **Flexible Configuration**: Customizable assignment rules and parameters

## 📊 Dashboard Features

### 🏠 Dashboard Overview
- Real-time assignment statistics and metrics
- Interactive charts showing student distribution
- Current assignment status and utilization rates

### 👥 Student Management
- Complete student database with filtering and search
- Student assignment status tracking
- Detailed student information display

### 👨‍🏫 Mentor Management  
- Mentor capacity and availability management
- Assignment workload visualization
- Department-wise mentor distribution

### 📋 Assignment Engine
- One-click automatic assignment execution
- Manual assignment override capabilities
- Assignment history and tracking

### 📈 Analytics Dashboard
- Assignment distribution analytics
- Mentor utilization statistics
- Department workload analysis

### 📥 Export & Reports
- **Assignment Summary**: Basic assignment statistics and overview
- **Detailed Mentor-Student Export**: Complete list of mentors with their assigned students
- Multiple format support (CSV, Excel, PDF, JSON)
- Automatic timestamping and file organization

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Automation-model-mentor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Dashboard**
   ```bash
   python start_dashboard.py
   ```
   
   Or directly:
   ```bash
   streamlit run streamlit_dashboard.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:8501`
   - Use the sidebar to navigate between different pages
   - Start with "Dashboard" for an overview

## 📁 Project Structure

```
Automation-model-mentor/
├── streamlit_dashboard.py    # Main Streamlit application
├── start_dashboard.py        # Simple launcher script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── README_STREAMLIT.md      # Detailed Streamlit documentation
├── src/                     # Core application modules
│   ├── models/             # Data models (Student, Mentor, Assignment)
│   ├── services/           # Business logic services
│   ├── utils/              # Utility functions and configuration
├── data/                   # CSV data files
│   ├── students.csv        # Student database
│   └── mentors.csv         # Mentor database
├── reports/                # Generated export files
├── tests/                  # Unit tests
├── .venv/                  # Virtual environment
```

## 🏗️ Architecture

### 1. **Data Layer**
- **Student Model**: Roll No, Name, Branch, Year, Contact Info
- **Mentor Model**: Faculty ID, Name, Department, Capacity, Availability  
- **Assignment Model**: Mentor-Student mappings with batch tracking
- **CSV Storage**: Simple file-based data persistence

### 2. **Service Layer**
- **DataService**: CRUD operations for students and mentors
- **AssignmentService**: Core assignment algorithm and logic
- **ExportService**: Multi-format report generation

### 3. **Presentation Layer** 
- **Streamlit Dashboard**: Interactive web interface
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Mobile-friendly interface

### 4. **Assignment Algorithm**
```python
# Sequential Assignment Logic
1. Load and validate student/mentor data
2. Sort students by roll number (ascending)
3. Group students into batches of 30
4. Assign each batch to next available mentor
5. Add remainder students to last mentor
6. Generate assignment summary and reports
```

## 🎯 Use Cases

- **Educational Institutions**: Assign students to academic mentors
- **Corporate Training**: Assign trainees to team leads  
- **Project Management**: Distribute team members across project managers
- **Event Management**: Assign participants to group facilitators

## 🔧 Configuration

The system is highly configurable through `src/utils/config.py`:

- **Batch Size**: Default 30 students per mentor (configurable)
- **Data Paths**: CSV file locations
- **Export Settings**: Output formats and file naming
- **Validation Rules**: Data quality constraints

## 📚 API Reference

For detailed API documentation and advanced usage, see `README_STREAMLIT.md`.

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🚀 Ready to get started?** Run `python start_dashboard.py` and open `http://localhost:8501` in your browser!

## Architecture

### 1. Input Layer (Data Collection)
- **Students Dataset**: Roll No, Name, Branch, Year, etc.
- **Mentors Dataset**: Faculty ID, Name, Department, Availability, etc.
- Data stored in CSV files for simplicity (can be extended to databases)

### 2. Processing Layer (Assignment Logic)
- Sort students by roll number (ascending)
- Batch allocation: 30 students per mentor
- Sequential mentor assignment
- Handle remainder students by adding to last batch

### 3. Output Layer (Visualization/Reports)
- Generate assignment mapping tables
- Export results to Excel/CSV/PDF formats
- Visual dashboard for administrators

### 4. Automation & Scalability
- Detect new students and assign to next available batch
- Handle mentor changes and redistribute students
- Configurable batch sizes and assignment rules

## Project Structure
```
Automation-model-mentor/
├── data/
│   ├── students.csv
│   ├── mentors.csv
│   └── assignments.csv
├── src/
│   ├── models/
│   │   ├── student.py
│   │   ├── mentor.py
│   │   └── assignment.py
│   ├── services/
│   │   ├── data_service.py
│   │   ├── assignment_service.py
│   │   └── export_service.py
│   ├── utils/
│   │   ├── config.py
│   │   └── validators.py
│   └── main.py
├── reports/
├── tests/
├── requirements.txt
└── README.md
```

## Usage
1. Add student data to `data/students.csv`
2. Add mentor data to `data/mentors.csv`
3. Run the assignment: `python src/main.py`
4. View results in `reports/` directory

## Features
- Automatic batch assignment (30 students per mentor)
- Handle remainder students in last batch
- Export to multiple formats (CSV, Excel, PDF)
- Visual dashboard
- Configurable settings
- Data validation
- Logging and error handling
