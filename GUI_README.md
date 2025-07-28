# Bengali License Plate Recognition GUI Application

This GUI application provides a user-friendly interface for real-time Bengali license plate detection and recognition using YOLO models.

## Features

### Main Interface
- **Video Display**: Real-time video feed with license plate detection overlay
- **Detection Panel**: Shows current detections and saved license plates
- **Configuration Panel**: Adjustable parameters for optimization

### Key Capabilities
1. **Real-time Processing**: Live camera feed or video file processing
2. **Stable Detection**: Filters out false positives by requiring consistent detections
3. **Model Flexibility**: Switch between different YOLO model sizes (s/m/n)
4. **Parameter Tuning**: Adjust confidence, resolution, frame skipping, etc.
5. **Data Export**: Save detections to JSON format
6. **Detection History**: Track and manage all recognized license plates

### Stability Algorithm
The application uses a smart stability detection system:
- Tracks recent detections in a rolling window
- Requires multiple consecutive similar detections before saving
- Configurable stability threshold (default: 5 frames)
- Prevents saving of temporary/incorrect detections

## Configuration Options

### Model Settings
- **Model Size**: Choose between 's' (small), 'm' (medium), 'n' (nano)
  - Small: Faster inference, lower accuracy
  - Medium: Balanced speed and accuracy
  - Nano: Fastest inference, basic accuracy

### Performance Settings
- **Frame Skip**: Process every Nth frame (1-10)
- **Confidence Threshold**: Detection confidence (0.1-0.9)
- **Image Size**: Processing resolution (320, 416, 640, 800)
- **Stability Frames**: Required consecutive detections (3-20)

## Usage Instructions

### 1. Starting the Application
```bash
python license_plate_gui.py
```

### 2. Camera/Video Input
- **Start Camera**: Use webcam for live detection
- **Load Video**: Process a video file from disk
- **Stop**: Stop current processing

### 3. Configuration
1. Adjust parameters in the Configuration panel
2. Click "Apply Settings" to update
3. Change model size to reload with different model

### 4. Monitoring Detections
- **Current Detection**: Shows real-time detection results
- **Saved License Plates**: List of stable detections with timestamps
- **Export**: Save detections to JSON file
- **Clear All/Delete Selected**: Manage saved detections

## Model Files Structure
```
model-s-detection/best.pt    # Small detection model
model-s-ocr/best.pt         # Small OCR model
model-m-detection/best.pt    # Medium detection model
model-m-ocr/best.pt         # Medium OCR model
model-n-detection/best.pt    # Nano detection model
model-n-ocr/best.pt         # Nano OCR model
```

## Character Mapping
The application recognizes:
- **Numbers**: 0-9
- **Bengali Characters**: Various Bengali letters and symbols
- **Location Names**: Bangladesh district and city names
- **Special Codes**: Metro, DA, etc.

## Performance Tips

### For Better Speed
- Use smaller model size ('s' or 'n')
- Increase frame skip (2-5)
- Reduce image size (320 or 416)
- Lower confidence threshold slightly

### For Better Accuracy
- Use larger model size ('m')
- Process every frame (frame skip = 1)
- Use higher resolution (640 or 800)
- Increase stability threshold (7-10)

### For CPU-only Systems
- Use nano model ('n')
- Set frame skip to 3-5
- Use 320 or 416 image size
- The application automatically detects and uses available hardware

## Output Format

### Saved Detections JSON
```json
[
  {
    "plate": "Dhaka Metro 123456",
    "timestamp": "2025-01-15 14:30:25",
    "confidence": "Stable"
  }
]
```

## Troubleshooting

### Common Issues
1. **Models not loading**: Ensure model files exist in correct directories
2. **Poor performance**: Reduce image size and increase frame skip
3. **Camera not working**: Check if camera is being used by another application
4. **Memory issues**: Use smaller model size and lower resolution

### System Requirements
- **Python**: 3.8+
- **RAM**: 4GB minimum, 8GB recommended
- **GPU**: CUDA-compatible GPU recommended but not required
- **Storage**: ~2GB for all model files

## Dependencies
All required packages are listed in `requirements.txt`. Key dependencies:
- OpenCV for video processing
- YOLO (Ultralytics) for detection
- Tkinter for GUI (usually included with Python)
- Pillow for image handling
- PyTorch for model inference

## License
This application is part of the Bengali License Plate Recognition project.
