#!/usr/bin/env python3
"""
Bengali License Plate Recognition GUI with Regex Filter and RTSP Support
Enhanced version with license plate format validation and RTSP video stream input
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import threading
import time
from collections import Counter, deque
import json
import os
import re
from datetime import datetime
from ultralytics import YOLO
import torch

class LicensePlateRTSPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bengali License Plate Recognition System with RTSP Support")
        
        # Make window responsive to screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set minimum size and calculate optimal size
        min_width, min_height = 1000, 600
        optimal_width = min(1400, int(screen_width * 0.9))
        optimal_height = min(800, int(screen_height * 0.9))
        
        self.root.geometry(f"{optimal_width}x{optimal_height}")
        self.root.minsize(min_width, min_height)
        
        # Center the window on screen
        x = (screen_width - optimal_width) // 2
        y = (screen_height - optimal_height) // 2
        self.root.geometry(f"{optimal_width}x{optimal_height}+{x}+{y}")
        
        # Initialize variables
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.detection_history = deque(maxlen=50)
        self.stable_detections = []
        self.saved_plates = []
        
        # RTSP variables (NEW!)
        self.rtsp_url = ""
        self.rtsp_username = ""
        self.rtsp_password = ""
        self.current_source_type = "camera"  # "camera", "video", "rtsp"
        
        # Model variables
        self.plate_detector = None
        self.char_recognizer = None
        
        # Configuration parameters
        self.config = {
            'model_size': 's',
            'frame_skip': 1,
            'confidence_threshold': 0.25,
            'image_size': 640,
            'stability_threshold': 5,
            'min_detection_length': 3,
        }
        
        # License plate format patterns
        self.license_patterns = {
            'standard': r'^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$',  # ChattoMetroGa 138707
            'metro_basic': r'^[A-Za-z]+Metro\s+\d{6}$',        # DhakaMetro 115636
            'district_simple': r'^(?!.*Metro)[A-Za-z]+\s+\d{2,6}$',  # Chatto 13 (excludes Metro)
            'custom': r'',
        }
        
        # Filter settings
        self.filter_settings = {
            'enabled': True,
            'pattern_type': 'standard',
            'custom_pattern': '',
            'allow_multiple_patterns': False,
        }
        
        # Character mapping
        self.char_map = {
            0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
            10: 'Metro', 11: 'A', 12: 'Bha', 13: 'Cha', 14: 'Chha', 15: 'Da', 16: 'DA', 17: 'E',
            18: 'Ga', 19: 'Gha', 20: 'Ha', 21: 'Ja', 22: 'Jha', 23: 'Ka', 24: 'Kha', 25: 'La',
            26: 'Ma', 27: 'Na', 28: 'Pa', 29: 'Sa', 30: 'Sha', 31: 'Ta', 32: 'THA', 33: 'Tha',
            34: 'U', 35: 'Bagerhat', 36: 'Bagura', 37: 'Bandarban', 38: 'Barguna', 39: 'Barisal',
            40: 'Bhola', 41: 'Brahmanbaria', 42: 'Chandpur', 43: 'Chapainawabganj', 44: 'Chatto',
            45: 'Chattogram', 46: 'Chuadanga', 47: 'Coxs Bazar', 48: 'Cumilla', 49: 'Dhaka',
            50: 'Dinajpur', 51: 'Faridpur', 52: 'Feni', 53: 'Gaibandha', 54: 'Gazipur',
            55: 'Gopalganj', 56: 'Habiganj', 57: 'Jamalpur', 58: 'Jessore', 59: 'Jhalokati',
            60: 'Jhenaidah', 61: 'Joypurhat', 62: 'Khagrachari', 63: 'Khulna', 64: 'Kishoreganj',
            65: 'Kurigram', 66: 'Kustia', 67: 'Lakshmipur', 68: 'Lalmonirhat', 69: 'Madaripur',
            70: 'Magura', 71: 'Manikganj', 72: 'Meherpur', 73: 'Moulvibazar', 74: 'Mymensingh',
            75: 'Naogaon', 76: 'Narail', 77: 'Narayanganj', 78: 'Narsingdi', 79: 'Natore',
            80: 'Netrokona', 81: 'Nilphamari', 82: 'Noakhali', 83: 'Pabna', 84: 'panchagarh',
            85: 'Patuakhali', 86: 'Pirojpur', 87: 'Raj', 88: 'Rajbari', 89: 'Rajshahi',
            90: 'Rangamati', 91: 'Rangpur', 92: 'Satkhira', 93: 'Shariatpur', 94: 'Sherpur',
            95: 'Sirajganj', 96: 'Sunamganj', 97: 'Sylhet', 98: 'Tangail', 99: 'Thakurgaon',
            100: 'Dha', 101: 'Ba'
        }
        
        self.create_widgets()
        self.load_models()
        
    def create_widgets(self):
        # Main container with responsive layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create main paned window for resizable panels
        main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Video display
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)  # Give more weight to video area
        
        # Video canvas with responsive sizing
        video_frame = ttk.Frame(left_frame)
        video_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=640, height=480)
        self.video_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons (ENHANCED WITH RTSP!)
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(pady=10)
        
        # First row of buttons
        control_row1 = ttk.Frame(control_frame)
        control_row1.pack(pady=5)
        
        self.start_btn = ttk.Button(control_row1, text="Start Camera", command=self.start_camera)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_video_btn = ttk.Button(control_row1, text="Load Video", command=self.load_video)
        self.load_video_btn.pack(side=tk.LEFT, padx=5)
        
        # NEW RTSP BUTTON!
        self.rtsp_btn = ttk.Button(control_row1, text="RTSP Stream", command=self.start_rtsp_stream)
        self.rtsp_btn.pack(side=tk.LEFT, padx=5)
        
        # Second row of buttons
        control_row2 = ttk.Frame(control_frame)
        control_row2.pack(pady=5)
        
        self.stop_btn = ttk.Button(control_row2, text="Stop", command=self.stop_capture)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # NEW RTSP CONFIG BUTTON!
        self.rtsp_config_btn = ttk.Button(control_row2, text="RTSP Config", command=self.configure_rtsp)
        self.rtsp_config_btn.pack(side=tk.LEFT, padx=5)
        
        # Status and FPS labels
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Status: Ready")
        self.status_label.pack()
        
        self.fps_label = ttk.Label(status_frame, text="FPS: 0")
        self.fps_label.pack()
        
        # NEW SOURCE INFO LABEL!
        self.source_label = ttk.Label(status_frame, text="Source: None", font=('Arial', 9))
        self.source_label.pack()
        
        # Right side - Scrollable control panel
        right_main_frame = ttk.Frame(main_paned)
        main_paned.add(right_main_frame, weight=1)  # Less weight for control panel
        
        # Create canvas and scrollbar for scrollable right panel
        canvas = tk.Canvas(right_main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now create all controls in the scrollable frame
        right_frame = self.scrollable_frame
        
        # ========================= NEW RTSP CONFIGURATION PANEL =========================
        rtsp_frame = ttk.LabelFrame(right_frame, text="📡 RTSP Configuration", padding=10)
        rtsp_frame.pack(fill=tk.X, pady=(0, 10))
        
        # RTSP URL
        ttk.Label(rtsp_frame, text="RTSP URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.rtsp_url_var = tk.StringVar(value="rtsp://")
        rtsp_url_entry = ttk.Entry(rtsp_frame, textvariable=self.rtsp_url_var, width=30)
        rtsp_url_entry.grid(row=0, column=1, columnspan=2, pady=2, padx=(5, 0), sticky=tk.W+tk.E)
        
        # Username (optional)
        ttk.Label(rtsp_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.rtsp_username_var = tk.StringVar()
        username_entry = ttk.Entry(rtsp_frame, textvariable=self.rtsp_username_var, width=15)
        username_entry.grid(row=1, column=1, pady=2, padx=(5, 0))
        
        # Password (optional)
        ttk.Label(rtsp_frame, text="Password:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.rtsp_password_var = tk.StringVar()
        password_entry = ttk.Entry(rtsp_frame, textvariable=self.rtsp_password_var, show="*", width=15)
        password_entry.grid(row=1, column=3, pady=2, padx=(5, 0))
        
        # Quick presets
        presets_frame = ttk.Frame(rtsp_frame)
        presets_frame.grid(row=2, column=0, columnspan=4, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(presets_frame, text="Quick Presets:").pack(side=tk.LEFT)
        ttk.Button(presets_frame, text="Local IP Cam", 
                  command=lambda: self.rtsp_url_var.set("rtsp://192.168.1.100:554/stream")).pack(side=tk.LEFT, padx=5)
        ttk.Button(presets_frame, text="Test Stream", 
                  command=lambda: self.rtsp_url_var.set("rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4")).pack(side=tk.LEFT, padx=5)
        
        # Test connection button
        test_rtsp_btn = ttk.Button(rtsp_frame, text="Test RTSP Connection", command=self.test_rtsp_connection)
        test_rtsp_btn.grid(row=3, column=0, columnspan=4, pady=5)
        
        # Connection status
        self.rtsp_status_label = ttk.Label(rtsp_frame, text="RTSP Status: Not connected", 
                                         font=('Arial', 9), foreground='red')
        self.rtsp_status_label.grid(row=4, column=0, columnspan=4, pady=2)
        # ==========================================================================
        
        # Configuration panel
        config_frame = ttk.LabelFrame(right_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Model size selection
        ttk.Label(config_frame, text="Model Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_size_var = tk.StringVar(value=self.config['model_size'])
        model_combo = ttk.Combobox(config_frame, textvariable=self.model_size_var, 
                                  values=['s', 'm', 'n'], state='readonly', width=15)
        model_combo.grid(row=0, column=1, pady=2, padx=(5, 0))
        model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Frame skip
        ttk.Label(config_frame, text="Frame Skip:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.frame_skip_var = tk.IntVar(value=self.config['frame_skip'])
        frame_skip_spin = ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.frame_skip_var, width=15)
        frame_skip_spin.grid(row=1, column=1, pady=2, padx=(5, 0))
        
        # Confidence threshold
        ttk.Label(config_frame, text="Confidence:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.confidence_var = tk.DoubleVar(value=self.config['confidence_threshold'])
        confidence_scale = ttk.Scale(config_frame, from_=0.1, to=0.9, variable=self.confidence_var, 
                                   orient=tk.HORIZONTAL, length=120)
        confidence_scale.grid(row=2, column=1, pady=2, padx=(5, 0))
        self.confidence_label = ttk.Label(config_frame, text=f"{self.config['confidence_threshold']:.2f}")
        self.confidence_label.grid(row=2, column=2, padx=(5, 0))
        confidence_scale.configure(command=self.update_confidence_label)
        
        # Image size
        ttk.Label(config_frame, text="Image Size:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.image_size_var = tk.IntVar(value=self.config['image_size'])
        size_combo = ttk.Combobox(config_frame, textvariable=self.image_size_var,
                                 values=[320, 416, 640, 800], state='readonly', width=15)
        size_combo.grid(row=3, column=1, pady=2, padx=(5, 0))
        
        # Stability threshold
        ttk.Label(config_frame, text="Stability Frames:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.stability_var = tk.IntVar(value=self.config['stability_threshold'])
        stability_spin = ttk.Spinbox(config_frame, from_=3, to=20, textvariable=self.stability_var, width=15)
        stability_spin.grid(row=4, column=1, pady=2, padx=(5, 0))
        
        # Apply button
        apply_btn = ttk.Button(config_frame, text="Apply Settings", command=self.apply_settings)
        apply_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # ========================= FILTER SECTION =========================
        # Filter configuration panel
        filter_frame = ttk.LabelFrame(right_frame, text="🔍 License Plate Filter", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Enable filter checkbox
        self.filter_enabled_var = tk.BooleanVar(value=self.filter_settings['enabled'])
        filter_check = ttk.Checkbutton(filter_frame, text="Enable Regex Filter", 
                                     variable=self.filter_enabled_var,
                                     command=self.toggle_filter)
        filter_check.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Pattern type selection
        ttk.Label(filter_frame, text="Pattern Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pattern_type_var = tk.StringVar(value=self.filter_settings['pattern_type'])
        pattern_combo = ttk.Combobox(filter_frame, textvariable=self.pattern_type_var,
                                   values=['standard', 'metro_basic', 'district_simple', 'custom'],
                                   state='readonly', width=12)
        pattern_combo.grid(row=1, column=1, pady=2, padx=(5, 0))
        pattern_combo.bind('<<ComboboxSelected>>', self.on_pattern_change)
        
        # Test filter button
        test_btn = ttk.Button(filter_frame, text="Test", command=self.test_filter)
        test_btn.grid(row=1, column=2, pady=2, padx=(5, 0))
        
        # Pattern preview
        ttk.Label(filter_frame, text="Pattern:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.pattern_preview_label = ttk.Label(filter_frame, text=self.get_current_pattern(),
                                             font=('Courier', 8), foreground='blue', wraplength=200)
        self.pattern_preview_label.grid(row=2, column=1, columnspan=2, pady=2, padx=(5, 0), sticky=tk.W)
        
        # Custom pattern entry (initially hidden)
        self.custom_pattern_label = ttk.Label(filter_frame, text="Custom:")
        self.custom_pattern_var = tk.StringVar(value=self.filter_settings['custom_pattern'])
        self.custom_pattern_entry = ttk.Entry(filter_frame, textvariable=self.custom_pattern_var, width=20)
        
        # Allow multiple patterns checkbox
        self.multiple_patterns_var = tk.BooleanVar(value=self.filter_settings['allow_multiple_patterns'])
        multiple_check = ttk.Checkbutton(filter_frame, text="Allow Multiple Patterns",
                                       variable=self.multiple_patterns_var)
        multiple_check.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Apply filter button
        apply_filter_btn = ttk.Button(filter_frame, text="Apply Filter Settings", command=self.apply_filter_settings)
        apply_filter_btn.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Update custom pattern visibility
        self.update_custom_pattern_visibility()
        # ===================================================================
        
        # Current detection panel
        current_frame = ttk.LabelFrame(right_frame, text="Current Detection", padding=10)
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create frame for scrollable text widget
        text_frame = ttk.Frame(current_frame)
        text_frame.pack(fill=tk.X, pady=5)
        
        # Create horizontally scrollable text widget for license plate display
        self.current_detection_text = tk.Text(text_frame, height=2, font=('Arial', 11, 'bold'),
                                            wrap=tk.NONE, bg='white', fg='black',
                                            state=tk.DISABLED, cursor='arrow')
        
        # Horizontal scrollbar for the text widget
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.current_detection_text.xview)
        self.current_detection_text.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack text widget and scrollbar
        self.current_detection_text.pack(side=tk.TOP, fill=tk.X)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize with default text
        self.update_detection_display("No detection")
        
        self.detection_confidence_label = ttk.Label(current_frame, text="Confidence: --")
        self.detection_confidence_label.pack()
        
        # Filter status
        self.filter_status_label = ttk.Label(current_frame, 
                                           text="Filter: Active" if self.filter_settings['enabled'] else "Filter: Disabled",
                                           font=('Arial', 9), 
                                           foreground='green' if self.filter_settings['enabled'] else 'red')
        self.filter_status_label.pack()
        
        # Saved detections panel with better height management
        saved_frame = ttk.LabelFrame(right_frame, text="Saved License Plates", padding=10)
        saved_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Listbox with scrollbar and fixed height
        list_frame = ttk.Frame(saved_frame)
        list_frame.pack(fill=tk.X)
        
        # Set a reasonable height for the listbox
        self.saved_listbox = tk.Listbox(list_frame, font=('Courier', 9), height=8)
        scrollbar_list = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.saved_listbox.yview)
        self.saved_listbox.configure(yscrollcommand=scrollbar_list.set)
        
        self.saved_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons for saved detections
        button_frame = ttk.Frame(saved_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_saved)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_btn = ttk.Button(button_frame, text="Export", command=self.export_saved)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Add some bottom padding to ensure scrolling works well
        bottom_spacer = ttk.Frame(right_frame, height=20)
        bottom_spacer.pack()

    # ========================= NEW RTSP METHODS =========================
    def configure_rtsp(self):
        """Open RTSP configuration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("RTSP Configuration")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # RTSP URL
        ttk.Label(main_frame, text="RTSP URL:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        url_entry = ttk.Entry(main_frame, textvariable=self.rtsp_url_var, width=60)
        url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Credentials frame
        cred_frame = ttk.LabelFrame(main_frame, text="Authentication (Optional)", padding=10)
        cred_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=2)
        username_entry = ttk.Entry(cred_frame, textvariable=self.rtsp_username_var, width=25)
        username_entry.grid(row=0, column=1, pady=2, padx=(10, 0))
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        password_entry = ttk.Entry(cred_frame, textvariable=self.rtsp_password_var, show="*", width=25)
        password_entry.grid(row=1, column=1, pady=2, padx=(10, 0))
        
        # Example URLs
        examples_frame = ttk.LabelFrame(main_frame, text="Example URLs", padding=10)
        examples_frame.pack(fill=tk.X, pady=(0, 10))
        
        examples = [
            "rtsp://192.168.1.100:554/stream",
            "rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0",
            "rtsp://username:password@camera_ip:554/live",
            "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"
        ]
        
        for i, example in enumerate(examples):
            ttk.Button(examples_frame, text=f"Example {i+1}", 
                      command=lambda url=example: self.rtsp_url_var.set(url)).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Test Connection", 
                  command=self.test_rtsp_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save & Close", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.RIGHT)
        
    def test_rtsp_connection(self):
        """Test RTSP connection"""
        rtsp_url = self.rtsp_url_var.get().strip()
        if not rtsp_url:
            messagebox.showwarning("Warning", "Please enter an RTSP URL")
            return
        
        # Build URL with credentials if provided
        final_url = self.build_rtsp_url()
        
        try:
            self.rtsp_status_label.config(text="RTSP Status: Testing connection...", foreground='orange')
            self.root.update()
            
            # Test connection
            test_cap = cv2.VideoCapture(final_url)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                test_cap.release()
                
                if ret and frame is not None:
                    self.rtsp_status_label.config(text="RTSP Status: ✅ Connection successful!", foreground='green')
                    messagebox.showinfo("Success", "RTSP connection test successful!")
                else:
                    self.rtsp_status_label.config(text="RTSP Status: ❌ No video data received", foreground='red')
                    messagebox.showerror("Error", "Connected but no video data received")
            else:
                self.rtsp_status_label.config(text="RTSP Status: ❌ Connection failed", foreground='red')
                messagebox.showerror("Error", "Failed to connect to RTSP stream")
                
        except Exception as e:
            self.rtsp_status_label.config(text=f"RTSP Status: ❌ Error: {str(e)[:30]}...", foreground='red')
            messagebox.showerror("Error", f"RTSP connection error: {str(e)}")
    
    def build_rtsp_url(self):
        """Build RTSP URL with credentials"""
        url = self.rtsp_url_var.get().strip()
        username = self.rtsp_username_var.get().strip()
        password = self.rtsp_password_var.get().strip()
        
        if username and password and "://" in url:
            # Insert credentials into URL
            protocol, rest = url.split("://", 1)
            if "@" not in rest:  # Only add if not already present
                url = f"{protocol}://{username}:{password}@{rest}"
        
        return url
    
    def start_rtsp_stream(self):
        """Start RTSP stream capture"""
        if not self.is_running:
            rtsp_url = self.rtsp_url_var.get().strip()
            if not rtsp_url:
                messagebox.showwarning("Warning", "Please enter an RTSP URL first")
                return
            
            final_url = self.build_rtsp_url()
            
            try:
                self.cap = cv2.VideoCapture(final_url)
                
                # Set buffer size to reduce latency
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                if self.cap.isOpened():
                    self.is_running = True
                    self.current_source_type = "rtsp"
                    
                    # Disable other input buttons
                    self.start_btn.config(state='disabled')
                    self.load_video_btn.config(state='disabled')
                    self.rtsp_btn.config(state='disabled')
                    
                    self.detection_thread = threading.Thread(target=self.process_video)
                    self.detection_thread.daemon = True
                    self.detection_thread.start()
                    
                    self.status_label.config(text="Status: RTSP stream running")
                    self.source_label.config(text=f"Source: RTSP - {rtsp_url[:50]}...")
                    self.rtsp_status_label.config(text="RTSP Status: ✅ Streaming", foreground='green')
                else:
                    messagebox.showerror("Error", "Could not connect to RTSP stream")
                    self.rtsp_status_label.config(text="RTSP Status: ❌ Connection failed", foreground='red')
                    
            except Exception as e:
                messagebox.showerror("Error", f"RTSP connection error: {str(e)}")
                self.rtsp_status_label.config(text=f"RTSP Status: ❌ Error", foreground='red')
    # =================================================================

    # ========================= FILTER METHODS =========================
    def update_detection_display(self, text):
        """Update the scrollable detection text widget"""
        self.current_detection_text.config(state=tk.NORMAL)
        self.current_detection_text.delete(1.0, tk.END)
        self.current_detection_text.insert(1.0, text)
        self.current_detection_text.config(state=tk.DISABLED)
        # Reset horizontal scroll to beginning
        self.current_detection_text.xview_moveto(0)
    
    def get_current_pattern(self):
        """Get the current regex pattern"""
        pattern_type = self.filter_settings['pattern_type']
        if pattern_type == 'custom':
            return self.filter_settings['custom_pattern'] or 'No custom pattern set'
        return self.license_patterns.get(pattern_type, '')
    
    def toggle_filter(self):
        """Toggle filter on/off"""
        self.filter_settings['enabled'] = self.filter_enabled_var.get()
        status = "Active" if self.filter_settings['enabled'] else "Disabled"
        color = 'green' if self.filter_settings['enabled'] else 'red'
        self.filter_status_label.config(text=f"Filter: {status}", foreground=color)
    
    def on_pattern_change(self, event=None):
        """Handle pattern type change"""
        self.filter_settings['pattern_type'] = self.pattern_type_var.get()
        self.pattern_preview_label.config(text=self.get_current_pattern())
        self.update_custom_pattern_visibility()
    
    def update_custom_pattern_visibility(self):
        """Show/hide custom pattern entry based on selection"""
        if self.pattern_type_var.get() == 'custom':
            self.custom_pattern_label.grid(row=3, column=0, sticky=tk.W, pady=2)
            self.custom_pattern_entry.grid(row=3, column=1, columnspan=2, pady=2, padx=(5, 0))
        else:
            self.custom_pattern_label.grid_remove()
            self.custom_pattern_entry.grid_remove()
    
    def test_filter(self):
        """Test the current filter with sample license plates"""
        test_plates = [
            "ChattoMetroGa 138707",  # Should pass standard
            "DhakaMetro 115636",     # Should pass metro_basic 
            "Chatto 13",             # Should pass district_simple
            "DhakaMetroGha 158013",  # Should pass standard
            "Metro 123456",          # Should fail all
            "InvalidPlate123",       # Should fail all
            "Dhaka 1234",            # Should pass district_simple
            "ChattoMetroKha 999999", # Should pass standard
        ]
        
        results = []
        for plate in test_plates:
            is_valid = self.validate_license_plate(plate)
            status = "✓ PASS" if is_valid else "✗ FAIL"
            results.append(f"{status}: {plate}")
        
        result_text = "Filter Test Results:\\n\\n" + "\\n".join(results)
        result_text += f"\\n\\nCurrent Pattern: {self.get_current_pattern()}"
        result_text += f"\\nFilter Enabled: {self.filter_settings['enabled']}"
        result_text += f"\\nMultiple Patterns: {self.filter_settings['allow_multiple_patterns']}"
        
        messagebox.showinfo("Filter Test Results", result_text)
    
    def apply_filter_settings(self):
        """Apply filter settings"""
        self.filter_settings['pattern_type'] = self.pattern_type_var.get()
        self.filter_settings['custom_pattern'] = self.custom_pattern_var.get()
        self.filter_settings['allow_multiple_patterns'] = self.multiple_patterns_var.get()
        self.filter_settings['enabled'] = self.filter_enabled_var.get()
        
        # Update pattern preview
        self.pattern_preview_label.config(text=self.get_current_pattern())
        
        # Update filter status
        status = "Active" if self.filter_settings['enabled'] else "Disabled"
        color = 'green' if self.filter_settings['enabled'] else 'red'
        self.filter_status_label.config(text=f"Filter: {status}", foreground=color)
        
        messagebox.showinfo("Filter Settings", "Filter settings applied successfully!")
    
    def validate_license_plate(self, plate_text):
        """Validate license plate against regex patterns"""
        if not self.filter_settings['enabled']:
            return True  # If filter is disabled, all plates are valid
        
        plate_text = plate_text.strip()
        if not plate_text:
            return False
        
        if self.filter_settings['allow_multiple_patterns']:
            # Check against all patterns
            patterns_to_check = []
            if self.filter_settings['pattern_type'] == 'custom':
                if self.filter_settings['custom_pattern']:
                    patterns_to_check.append(self.filter_settings['custom_pattern'])
            else:
                # Check against all predefined patterns
                patterns_to_check.extend([
                    self.license_patterns['standard'],
                    self.license_patterns['metro_basic'],
                    self.license_patterns['district_simple']
                ])
        else:
            # Check against selected pattern only
            if self.filter_settings['pattern_type'] == 'custom':
                patterns_to_check = [self.filter_settings['custom_pattern']] if self.filter_settings['custom_pattern'] else []
            else:
                patterns_to_check = [self.license_patterns[self.filter_settings['pattern_type']]]
        
        # Test against patterns
        for pattern in patterns_to_check:
            if pattern:  # Only test non-empty patterns
                try:
                    if re.match(pattern, plate_text, re.IGNORECASE):
                        return True
                except re.error:
                    # Invalid regex pattern
                    continue
        
        return False
    # ===================================================================
        
    def load_models(self):
        """Load YOLO models based on current configuration"""
        try:
            model_size = self.config['model_size']
            # Use absolute paths to ensure models are found
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            detection_path = os.path.join(base_dir, f"model-{model_size}-detection", "best.pt")
            ocr_path = os.path.join(base_dir, f"model-{model_size}-ocr", "best.pt")
            
            # Check if files exist
            if not os.path.exists(detection_path):
                raise FileNotFoundError(f"Detection model not found: {detection_path}")
            if not os.path.exists(ocr_path):
                raise FileNotFoundError(f"OCR model not found: {ocr_path}")
            
            self.plate_detector = YOLO(detection_path)
            self.char_recognizer = YOLO(ocr_path)
            
            # Use GPU if available
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.plate_detector.to(device)
            self.char_recognizer.to(device)
            
            self.status_label.config(text=f"Status: Models loaded (Size: {model_size.upper()}, Device: {device})")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")
            self.status_label.config(text="Status: Model loading failed")
            return False
    
    def on_model_change(self, event=None):
        """Handle model size change"""
        self.config['model_size'] = self.model_size_var.get()
        self.load_models()
    
    def update_confidence_label(self, value):
        """Update confidence label"""
        self.confidence_label.config(text=f"{float(value):.2f}")
    
    def apply_settings(self):
        """Apply current settings"""
        self.config['frame_skip'] = self.frame_skip_var.get()
        self.config['confidence_threshold'] = self.confidence_var.get()
        self.config['image_size'] = self.image_size_var.get()
        self.config['stability_threshold'] = self.stability_var.get()
        
        messagebox.showinfo("Settings", "Settings applied successfully!")
    
    def start_camera(self):
        """Start camera capture"""
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_running = True
                self.current_source_type = "camera"
                
                # Disable other input buttons
                self.start_btn.config(state='disabled')
                self.load_video_btn.config(state='disabled')
                self.rtsp_btn.config(state='disabled')
                
                self.detection_thread = threading.Thread(target=self.process_video)
                self.detection_thread.daemon = True
                self.detection_thread.start()
                self.status_label.config(text="Status: Camera running")
                self.source_label.config(text="Source: Local Camera")
            else:
                messagebox.showerror("Error", "Could not open camera")
    
    def load_video(self):
        """Load video file"""
        if not self.is_running:
            file_path = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
            )
            if file_path:
                self.cap = cv2.VideoCapture(file_path)
                if self.cap.isOpened():
                    self.is_running = True
                    self.current_source_type = "video"
                    
                    # Disable other input buttons
                    self.start_btn.config(state='disabled')
                    self.load_video_btn.config(state='disabled')
                    self.rtsp_btn.config(state='disabled')
                    
                    self.detection_thread = threading.Thread(target=self.process_video)
                    self.detection_thread.daemon = True
                    self.detection_thread.start()
                    self.status_label.config(text=f"Status: Processing video")
                    self.source_label.config(text=f"Source: Video - {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", "Could not open video file")
    
    def stop_capture(self):
        """Stop video capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        
        # Re-enable all input buttons
        self.start_btn.config(state='normal')
        self.load_video_btn.config(state='normal')
        self.rtsp_btn.config(state='normal')
        
        self.status_label.config(text="Status: Stopped")
        self.source_label.config(text="Source: None")
        self.video_canvas.delete("all")
        
        # Update RTSP status if it was an RTSP stream
        if self.current_source_type == "rtsp":
            self.rtsp_status_label.config(text="RTSP Status: Disconnected", foreground='red')
    
    def process_video(self):
        """Main video processing loop"""
        frame_count = 0
        last_time = time.time()
        
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                if self.current_source_type == "video":
                    # Video ended
                    break
                elif self.current_source_type == "rtsp":
                    # RTSP connection lost, try to reconnect
                    print("RTSP connection lost, attempting to reconnect...")
                    self.rtsp_status_label.config(text="RTSP Status: Reconnecting...", foreground='orange')
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    break
            
            frame_count += 1
            
            # Skip frames based on configuration
            if frame_count % self.config['frame_skip'] != 0:
                continue
            
            # Calculate FPS
            current_time = time.time()
            if current_time - last_time >= 1.0:
                fps = frame_count / (current_time - last_time)
                self.fps_label.config(text=f"FPS: {fps:.1f}")
                frame_count = 0
                last_time = current_time
            
            # Process frame for license plate detection
            processed_frame = self.detect_license_plate(frame.copy())
            
            # Display frame
            self.display_frame(processed_frame)
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.01)
        
        self.stop_capture()
    
    def detect_license_plate(self, frame):
        """Detect and recognize license plates in frame"""
        if not self.plate_detector or not self.char_recognizer:
            return frame
        
        try:
            # Detect license plates
            plate_results = self.plate_detector(
                frame, 
                conf=self.config['confidence_threshold'],
                imgsz=self.config['image_size'],
                verbose=False
            )
            
            current_detections = []
            
            for plate in plate_results:
                if not hasattr(plate.boxes, 'xyxy') or len(plate.boxes.xyxy) == 0:
                    continue
                    
                boxes = plate.boxes.xyxy
                
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)
                    plate_img = frame[y1:y2, x1:x2]
                    
                    if plate_img.size == 0:
                        continue
                    
                    # Recognize characters in the plate
                    char_results = self.char_recognizer(
                        plate_img,
                        conf=self.config['confidence_threshold'],
                        imgsz=self.config['image_size'],
                        verbose=False
                    )
                    
                    detected_chars = []
                    for char in char_results:
                        if not hasattr(char.boxes, 'xyxy') or len(char.boxes.xyxy) == 0:
                            continue
                            
                        for cbox in char.boxes:
                            cx1, cy1, cx2, cy2 = cbox.xyxy[0]
                            class_id = int(cbox.cls)
                            center_x = (cx1 + cx2) / 2
                            detected_chars.append((center_x, class_id))
                    
                    if len(detected_chars) >= self.config['min_detection_length']:
                        # Separate and sort characters
                        label1, label2 = [], []
                        for center_x, class_id in detected_chars:
                            if class_id in range(0, 10):  # Numbers
                                label2.append((center_x, class_id))
                            else:  # Letters
                                label1.append((center_x, class_id))
                        
                        label1.sort(key=lambda x: x[0])
                        label2.sort(key=lambda x: x[0])
                        
                        # Convert to text
                        plate_text = "".join([self.char_map.get(c[1], '?') for c in label1]) + " " + \
                                   "".join([self.char_map.get(c[1], '?') for c in label2])
                        
                        plate_text = plate_text.strip()
                        if plate_text and plate_text != " ":
                            current_detections.append(plate_text)
                            
                            # Draw bounding box and text
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, plate_text, (x1, y1 - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Update current detection display
            if current_detections:
                self.update_detection_display(current_detections[0])
                self.detection_confidence_label.config(text="Active Detection")
                
                # Add to detection history for stability analysis
                self.detection_history.append(current_detections[0])
                self.check_stable_detection()
            else:
                self.update_detection_display("No detection")
                self.detection_confidence_label.config(text="--")
                
        except Exception as e:
            print(f"Detection error: {e}")
        
        return frame
    
    def check_stable_detection(self):
        """Check for stable detections and save them"""
        if len(self.detection_history) < self.config['stability_threshold']:
            return
        
        # Get recent detections
        recent = list(self.detection_history)[-self.config['stability_threshold']:]
        
        # Check if we have enough similar detections
        counter = Counter(recent)
        most_common = counter.most_common(1)
        
        if most_common and most_common[0][1] >= self.config['stability_threshold']:
            stable_plate = most_common[0][0]
            
            # Check if this plate is already in our saved list (avoid duplicates)
            if stable_plate not in [item['plate'] for item in self.saved_plates]:
                self.save_detection(stable_plate)
    
    def save_detection(self, plate_text):
        """Save a stable detection if it passes the filter"""
        # Validate against filter
        if not self.validate_license_plate(plate_text):
            print(f"🚫 Filtered out invalid plate format: {plate_text}")
            print(f"   Filter enabled: {self.filter_settings['enabled']}")
            print(f"   Pattern type: {self.filter_settings['pattern_type']}")
            print(f"   Current pattern: {self.get_current_pattern()}")
            return False
        
        # Check if this plate is already in our saved list
        if plate_text in [item['plate'] for item in self.saved_plates]:
            print(f"Plate already saved: {plate_text}")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        detection = {
            'plate': plate_text,
            'timestamp': timestamp,
            'confidence': 'Stable',
            'source': self.current_source_type,  # NEW!
            'filter_pattern': self.filter_settings['pattern_type'],
            'filter_enabled': self.filter_settings['enabled']
        }
        
        self.saved_plates.append(detection)
        self.saved_listbox.insert(tk.END, f"{timestamp} - {plate_text}")
        
        # Auto-scroll to bottom
        self.saved_listbox.see(tk.END)
        
        print(f"✅ Saved stable detection: {plate_text} at {timestamp} from {self.current_source_type}")
        return True
    
    def display_frame(self, frame):
        """Display frame in the canvas with responsive sizing"""
        if frame is None:
            return
        
        # Update canvas to get current size
        self.video_canvas.update_idletasks()
        
        # Resize frame to fit canvas
        height, width = frame.shape[:2]
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        # Ensure minimum canvas size
        if canvas_width < 100:
            canvas_width = 640
        if canvas_height < 100:
            canvas_height = 480
            
        # Calculate scaling factor to maintain aspect ratio
        scale = min(canvas_width/width, canvas_height/height, 1.0)  # Don't upscale
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Only resize if dimensions are valid
        if new_width > 0 and new_height > 0:
            frame_resized = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB and then to ImageTk
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # Clear canvas and display new frame centered
            self.video_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.video_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # Keep a reference to prevent garbage collection
            self.video_canvas.image = photo
    
    def clear_saved(self):
        """Clear all saved detections"""
        if messagebox.askyesno("Confirm", "Clear all saved detections?"):
            self.saved_plates.clear()
            self.saved_listbox.delete(0, tk.END)
    
    def delete_selected(self):
        """Delete selected detection"""
        selection = self.saved_listbox.curselection()
        if selection:
            index = selection[0]
            self.saved_listbox.delete(index)
            if index < len(self.saved_plates):
                del self.saved_plates[index]
    
    def export_saved(self):
        """Export saved detections to JSON file"""
        if not self.saved_plates:
            messagebox.showwarning("Warning", "No detections to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Detections",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                export_data = {
                    'export_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'filter_settings': self.filter_settings,
                    'rtsp_url': self.rtsp_url_var.get() if self.rtsp_url_var.get() else None,  # NEW!
                    'detections': self.saved_plates
                }
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                messagebox.showinfo("Success", f"Detections exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.cap:
            self.cap.release()


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = LicensePlateRTSPGUI(root)
    
    def on_closing():
        app.stop_capture()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Show initial message with RTSP info
    screen_width = root.winfo_screenwidth()
    if screen_width < 1200:  # Smaller screen
        messagebox.showinfo("Bengali License Plate Recognition with RTSP", 
                           "Enhanced GUI with RTSP Support\\n\\n" +
                           "NEW FEATURES:\\n" +
                           "• RTSP video stream input\\n" +
                           "• Camera, Video & RTSP sources\\n" +
                           "• Pattern validation\\n" +
                           "• Filter testing\\n" +
                           "• Scrollable text display\\n\\n" +
                           "Configure RTSP in the right panel\\n" +
                           "Use scroll wheel for navigation")
    else:  # Larger screen
        messagebox.showinfo("Bengali License Plate Recognition with RTSP", 
                           "Enhanced GUI with RTSP Stream Support\\n\\n" +
                           "NEW FEATURES:\\n" +
                           "• RTSP video stream input with authentication\\n" +
                           "• Multiple input sources: Camera, Video, RTSP\\n" +
                           "• Pattern-based license plate validation\\n" +
                           "• Multiple regex patterns supported\\n" +
                           "• Filter testing functionality\\n" +
                           "• Horizontally scrollable text display\\n\\n" +
                           "Configure RTSP streams in the configuration panel\\n" +
                           "Default: Only 'ChattoMetroGa 138707' format allowed")
    
    root.mainloop()


if __name__ == "__main__":
    main()
