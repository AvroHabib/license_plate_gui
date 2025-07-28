#!/usr/bin/env python3
"""
Test script to verify GUI dependencies and launch the application
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'tkinter',
        'cv2',
        'PIL',
        'threading',
        'time',
        'collections',
        'json',
        'datetime',
        'ultralytics',
        'torch'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'cv2':
                import cv2
            elif module == 'PIL':
                from PIL import Image, ImageTk
            elif module == 'ultralytics':
                from ultralytics import YOLO
            elif module == 'torch':
                import torch
            else:
                __import__(module)
            print(f"✓ {module} - OK")
        except ImportError as e:
            print(f"✗ {module} - MISSING ({e})")
            missing_modules.append(module)
    
    return missing_modules

def check_model_files():
    """Check if model files exist"""
    model_sizes = ['s', 'm', 'n']
    model_types = ['detection', 'ocr']
    
    missing_models = []
    
    for size in model_sizes:
        for model_type in model_types:
            model_path = f"model-{size}-{model_type}/best.pt"
            if os.path.exists(model_path):
                print(f"✓ {model_path} - Found")
            else:
                print(f"✗ {model_path} - Missing")
                missing_models.append(model_path)
    
    return missing_models

def main():
    print("Bengali License Plate Recognition GUI - Dependency Check")
    print("=" * 60)
    
    print("\n1. Checking Python modules...")
    missing_modules = check_dependencies()
    
    print("\n2. Checking model files...")
    missing_models = check_model_files()
    
    print("\n" + "=" * 60)
    
    if missing_modules:
        print("❌ Missing Python modules:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nPlease install missing modules and try again.")
        return False
    
    if missing_models:
        print("⚠️  Missing model files:")
        for model in missing_models:
            print(f"   - {model}")
        print("\nSome models are missing. The GUI will still work with available models.")
    
    print("✅ Dependencies check completed!")
    
    # Ask user if they want to launch the GUI
    try:
        response = input("\nDo you want to launch the GUI application? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\nLaunching GUI application...")
            from license_plate_gui import main as gui_main
            gui_main()
        else:
            print("GUI launch cancelled.")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    
    return True

if __name__ == "__main__":
    main()
