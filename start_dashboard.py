"""
Start script for the Streamlit dashboard
"""

import subprocess
import sys
import os

def main():
    """Start the Streamlit dashboard"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the project directory
    os.chdir(script_dir)
    
    # Get the virtual environment Python path
    venv_python = os.path.join(script_dir, '.venv', 'Scripts', 'python.exe')
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found. Please run 'configure_python_environment' first.")
        return
    
    print("🎓 Starting Student-Mentor Assignment Dashboard...")
    print("📊 This will open in your browser at http://localhost:8501")
    print("💡 Press Ctrl+C to stop the server")
    
    try:
        # Start Streamlit
        subprocess.run([
            venv_python, 
            '-m', 
            'streamlit', 
            'run', 
            'streamlit_dashboard.py'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting dashboard: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")

if __name__ == "__main__":
    main()
