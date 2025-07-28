#!/usr/bin/env python3
"""
Setup script for Ghost of Space Enhanced Edition
"""
import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs", "assets", "assets/images", "assets/sounds", "assets/fonts"]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f"Created directory: {directory}")


def test_installation():
    """Test if the installation is working"""
    print("Testing installation...")
    try:
        import pygame
        import sqlite3
        print("✓ All required modules are available")
        
        # Test pygame initialization
        pygame.init()
        pygame.quit()
        print("✓ Pygame initialization test passed")
        
        return True
    except ImportError as e:
        print(f"✗ Missing module: {e}")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("Ghost of Space Enhanced Edition - Setup")
    print("=" * 45)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\nSetup completed with warnings. Some features may not work properly.")
    else:
        print("\n✓ Setup completed successfully!")
    
    print("\nTo run the game:")
    print("  python ghost_of_space.py")
    print("\nTo migrate old scores:")
    print("  python migrate_scores.py")
    print("\nEnjoy playing Ghost of Space Enhanced Edition!")


if __name__ == "__main__":
    main()