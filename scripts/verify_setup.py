"""
Environment Verification Script for Chemical Equipment Visualizer
Run this to verify your Python environment is correctly set up.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def verify_environment():
    """Verify the Python environment setup."""
    
    print_header("Python Environment Verification")
    
    # Check Python version
    print_info("Checking Python version...")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"   Python Version: {version_str}")
    
    if version.major == 3 and version.minor == 11:
        print_success(f"Python 3.11.x detected ({version_str})")
    else:
        print_error(f"Expected Python 3.11.x, but found {version_str}")
        print("   Please activate the correct virtual environment")
        return False
    
    # Check if in virtual environment
    print_info("\nChecking virtual environment...")
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_success("Running inside virtual environment")
        print(f"   Virtual Env: {sys.prefix}")
    else:
        print_error("Not running in virtual environment")
        print("   Run: .venv\\Scripts\\Activate.ps1")
        return False
    
    # Check required packages
    print_info("\nChecking required packages...")
    
    import subprocess
    import json
    
    try:
        # Use pip list to get accurate package information
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        installed_packages = {pkg['name'].lower(): pkg['version'] for pkg in json.loads(result.stdout)}
        
        required_packages = {
            'django': '4.2.7',
            'djangorestframework': '3.14.0',
            'djangorestframework-simplejwt': '5.3.0',
            'django-cors-headers': '4.3.1',
            'pandas': '2.1.3',
            'numpy': '1.26.2',
            'reportlab': '4.0.7',
            'python-decouple': '3.8',
            'pillow': '10.1.0',
        }
        
        all_packages_ok = True
        for package, expected_version in required_packages.items():
            package_lower = package.lower()
            if package_lower in installed_packages:
                version = installed_packages[package_lower]
                print_success(f"{package.ljust(35)} {version}")
            else:
                print_error(f"{package.ljust(35)} NOT INSTALLED")
                all_packages_ok = False
        
        if not all_packages_ok:
            print("\n   Run: pip install -r backend\\requirements.txt")
            return False
    except Exception as e:
        print_error(f"Error checking packages: {str(e)}")
        return False
    
    # Check project structure
    print_info("\nChecking project structure...")
    project_root = Path(__file__).parent
    required_paths = [
        'backend/manage.py',
        'backend/requirements.txt',
        'frontend/package.json',
        'desktop/main.py',
        'docs/sample_data.csv',
    ]
    
    all_paths_ok = True
    for path in required_paths:
        full_path = project_root / path
        if full_path.exists():
            print_success(f"{path}")
        else:
            print_error(f"{path} - NOT FOUND")
            all_paths_ok = False
    
    if not all_paths_ok:
        print_error("Some required files are missing")
        return False
    
    # Check Django setup
    print_info("\nChecking Django configuration...")
    try:
        sys.path.insert(0, str(project_root / 'backend'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equipment_backend.settings')
        
        import django
        django.setup()
        
        print_success("Django configuration loaded successfully")
        print(f"   Django Version: {django.get_version()}")
        
        # Check database
        from django.db import connection
        from django.contrib.auth.models import User
        
        try:
            user_count = User.objects.count()
            print_success(f"Database accessible ({user_count} users)")
        except Exception as e:
            print_error(f"Database error: {str(e)}")
            print("   Run: python manage.py migrate")
            
    except Exception as e:
        print_error(f"Django setup error: {str(e)}")
        print("   Check backend/equipment_backend/settings.py")
    
    # Summary
    print_header("Verification Complete")
    print_success("Environment is correctly configured!")
    print_info("\nNext Steps:")
    print("   1. cd backend")
    print("   2. python manage.py migrate")
    print("   3. python manage.py createsuperuser")
    print("   4. python manage.py runserver")
    print("\n   Then open: http://localhost:8000/admin")
    
    return True

if __name__ == "__main__":
    try:
        verify_environment()
    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        sys.exit(1)
