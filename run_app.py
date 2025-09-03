#!/usr/bin/env python3
"""
Inventory Management System Launcher
====================================

This script launches the Inventory Management System.
Choose between Desktop (Tkinter) or Web (Flask) version.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['tkinter']  # tkinter comes with Python
    missing_packages = []
    
    try:
        import tkinter
    except ImportError:
        missing_packages.append('tkinter')
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages and try again.")
        return False
    
    return True

def run_desktop_app():
    """Run the desktop Tkinter application"""
    print("🚀 Starting Inventory Management System (Desktop)...")
    print("=" * 50)
    
    try:
        from main_app import main
        main()
    except ImportError as e:
        print(f"❌ Error importing main application: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False
    
    return True

def run_web_app():
    """Run the web Flask application"""
    print("🌐 Starting Inventory Management System (Web)...")
    print("=" * 50)
    
    try:
        from web_app import app
        print("✅ Flask application loaded successfully")
        print("🌐 Starting web server...")
        print("📱 Access the application at: http://localhost:5000")
        print("👤 Login credentials: admin / admin")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        return True
    except ImportError as e:
        print(f"❌ Error importing Flask application: {e}")
        print("💡 Make sure Flask is installed: pip install flask")
        return False
    except Exception as e:
        print(f"❌ Error running web application: {e}")
        return False

def show_menu():
    """Show application menu"""
    print("🏪 Inventory Management System")
    print("=" * 40)
    print("Choose your preferred interface:")
    print()
    print("1. 🖥️  Desktop Application (Tkinter)")
    print("2. 🌐 Web Application (Flask)")
    print("3. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                return 'desktop'
            elif choice == '2':
                return 'web'
            elif choice == '3':
                return 'exit'
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return 'exit'

def main():
    """Main launcher function"""
    print("🏪 Inventory Management System Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Show menu and get user choice
    choice = show_menu()
    
    if choice == 'desktop':
        success = run_desktop_app()
        if not success:
            print("\n❌ Failed to start desktop application")
            sys.exit(1)
    elif choice == 'web':
        success = run_web_app()
        if not success:
            print("\n❌ Failed to start web application")
            sys.exit(1)
    elif choice == 'exit':
        print("👋 Goodbye!")
        sys.exit(0)
    
    print("\n✅ Application closed successfully")

if __name__ == "__main__":
    main()