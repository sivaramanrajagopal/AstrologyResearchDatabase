#!/usr/bin/env python3
"""
Setup script for Astrological Birth Chart Database
This script helps users install dependencies and run the application.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🌟 Astrological Birth Chart Database Setup 🌟")
    print("=" * 60)
    print("Collecting 400 native birth charts for astrological research")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["data", "static/css", "static/js", "templates"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def check_files():
    """Check if all required files exist"""
    print("\n📋 Checking required files...")
    required_files = [
        "app.py",
        "requirements.txt",
        "templates/base.html",
        "templates/index.html",
        "templates/add_birth_chart.html",
        "templates/view_charts.html",
        "templates/statistics.html",
        "static/css/style.css",
        "static/js/script.js"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        print("Please ensure all files are present before running the application")
        return False
    return True

def run_application():
    """Run the Flask application"""
    print("\n🚀 Starting the application...")
    print("The application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def show_instructions():
    """Show usage instructions"""
    print("\n📖 Usage Instructions:")
    print("1. Add Birth Charts:")
    print("   - Go to 'Add Chart' page")
    print("   - Fill in all required fields")
    print("   - Select appropriate research category")
    print("   - Use consistent researcher ID")
    
    print("\n2. View and Export Data:")
    print("   - Use 'View Charts' to browse data")
    print("   - Filter by research category")
    print("   - Export data in CSV or JSON format")
    
    print("\n3. Research Categories:")
    print("   - Business Success")
    print("   - Medical Conditions (Autism, ADHD, etc.)")
    print("   - IT/Technology Careers")
    print("   - Creative Arts, Sports, Education, etc.")
    
    print("\n4. Best Practices:")
    print("   - Ensure accurate birth time (within 15 minutes)")
    print("   - Verify birth location details")
    print("   - Respect privacy and confidentiality")
    print("   - Use for research purposes only")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Check files
    if not check_files():
        print("\n⚠️  Some files are missing. Please ensure all files are present.")
        return
    
    print("\n✅ Setup completed successfully!")
    
    # Show instructions
    show_instructions()
    
    # Ask if user wants to run the application
    print("\n" + "=" * 60)
    response = input("Would you like to start the application now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        run_application()
    else:
        print("\nTo start the application later, run:")
        print("python app.py")
        print("\nOr run this setup script again:")
        print("python setup.py")

if __name__ == "__main__":
    main() 