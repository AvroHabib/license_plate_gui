# 🔍 Enhanced Bengali License Plate Recognition GUI with Regex Filter

## 🎉 NEW FEATURES ADDED

### ✨ License Plate Format Validation
The GUI now includes a powerful regex filter system that validates license plate formats before saving them. This prevents invalid detections like "Chatto 13" from being saved when you only want the standard format like "ChattoMetroGa 138707".

### 🔧 Filter Control Panel
A new "License Plate Filter" panel has been added to the sidebar with the following controls:

#### Filter Settings
- **Enable Regex Filter**: Toggle the filter on/off
- **Pattern Type**: Choose from predefined patterns or create custom ones
- **Test Button**: Test the current filter against sample license plates
- **Apply Filter Settings**: Apply your filter configuration

#### Available Pattern Types

1. **Standard Pattern** (Default)
   - Format: `[District]Metro[Letter] [6-digit number]`
   - Example: `ChattoMetroGa 138707`
   - Regex: `^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$`

2. **Metro Basic Pattern**
   - Format: `[District]Metro [6-digit number]`
   - Example: `DhakaMetro 115636`
   - Regex: `^[A-Za-z]+Metro\s+\d{6}$`

3. **District Simple Pattern**
   - Format: `[District] [2-6 digit number]`
   - Example: `Chatto 13`, `Dhaka 1234`
   - Regex: `^[A-Za-z]+\s+\d{2,6}$`

4. **Custom Pattern**
   - Define your own regex pattern
   - Useful for specific requirements

### 🧪 Filter Testing
- Click "Test" button to see how your filter performs against sample license plates
- Shows which plates pass/fail your current filter
- Displays the current regex pattern being used

### 📊 Enhanced Saving Logic
- Only license plates that match the active filter pattern are saved
- Console shows when plates are filtered out with reasons
- Saved detections include filter information in export

### 🎛️ Filter Status Display
- Real-time filter status shown in the Current Detection panel
- Green "Filter: Active" when enabled
- Red "Filter: Disabled" when turned off

## 🚀 How to Use the New Filter

### 1. Basic Usage
1. Launch the GUI: `python license_plate_gui_filtered.py`
2. The filter is enabled by default with "Standard" pattern
3. Only plates like "ChattoMetroGa 138707" will be saved
4. Plates like "Chatto 13" will be filtered out

### 2. Customizing Filter
1. In the "License Plate Filter" panel:
   - Choose your desired pattern type
   - Test it using the "Test" button
   - Click "Apply Filter Settings"

### 3. Allowing Multiple Formats
1. Check "Allow Multiple Patterns" 
2. This will accept any of the three predefined patterns
3. Both "ChattoMetroGa 138707" AND "Chatto 13" will be saved

### 4. Creating Custom Patterns
1. Select "Custom" from Pattern Type
2. Enter your regex pattern in the custom field
3. Test and apply the settings

## 📈 Filter Examples

### Example 1: Only Standard Format
```
Pattern Type: standard
Filter: ^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$

✅ PASS: ChattoMetroGa 138707
✅ PASS: DhakaMetroGha 158013
❌ FAIL: DhakaMetro 115636
❌ FAIL: Chatto 13
```

### Example 2: Multiple Patterns Allowed
```
Allow Multiple Patterns: ✓
Pattern Type: Any

✅ PASS: ChattoMetroGa 138707
✅ PASS: DhakaMetro 115636
✅ PASS: Chatto 13
❌ FAIL: InvalidPlate123
```

### Example 3: Custom Pattern (6-digit numbers only)
```
Pattern Type: custom
Custom Pattern: .*\d{6}.*

✅ PASS: ChattoMetroGa 138707
✅ PASS: DhakaMetro 115636
❌ FAIL: Chatto 13
```

## 🔧 Technical Details

### Regex Patterns Used
- **Standard**: `^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$`
- **Metro Basic**: `^[A-Za-z]+Metro\s+\d{6}$`
- **District Simple**: `^[A-Za-z]+\s+\d{2,6}$`

### Filter Validation Process
1. License plate detected by YOLO
2. Text extracted and cleaned
3. Compared against active regex pattern(s)
4. Only matching plates are saved to the list
5. Filtered plates are logged to console

### Enhanced Export Format
Exported JSON now includes:
```json
{
  "export_timestamp": "2025-01-15 14:30:25",
  "filter_settings": {
    "enabled": true,
    "pattern_type": "standard",
    "custom_pattern": "",
    "allow_multiple_patterns": false
  },
  "detections": [
    {
      "plate": "ChattoMetroGa 138707",
      "timestamp": "2025-01-15 14:25:10",
      "confidence": "Stable",
      "filter_pattern": "standard",
      "filter_enabled": true
    }
  ]
}
```

## 🎯 Benefits

### ✅ Improved Accuracy
- Eliminates false positives and partial detections
- Only saves complete, valid license plate formats
- Customizable validation rules

### ✅ Better Data Quality
- Consistent format in saved detections
- Easier to process exported data
- Reduced manual cleanup required

### ✅ Flexible Configuration
- Multiple predefined patterns
- Custom regex support
- Real-time testing and validation

### ✅ User-Friendly
- Visual filter status indicators
- Test functionality with sample data
- Clear pattern descriptions

## 🔄 Migration from Old Version

If you have the old GUI version:
1. Use `license_plate_gui_filtered.py` (new enhanced version)
2. Your old settings will work the same way
3. New filter features are additional - won't break existing workflow
4. To get old behavior: disable the filter or use "Allow Multiple Patterns"

## 🐛 Troubleshooting

### Filter Not Working
- Check if filter is enabled (green "Filter: Active")
- Test your pattern with the "Test" button
- Verify regex syntax for custom patterns

### Too Many Plates Filtered Out
- Try "Allow Multiple Patterns"
- Use a more permissive pattern like "district_simple"
- Check if your expected format matches any predefined pattern

### Custom Pattern Issues
- Test regex patterns online first
- Remember to escape special characters
- Use the "Test" button to validate

## 📝 Console Output Examples

When filter is working:
```
✅ Saved stable detection: ChattoMetroGa 138707 at 2025-01-15 14:30:25
🚫 Filtered out invalid plate format: Chatto 13
   Filter enabled: True
   Pattern type: standard
   Current pattern: ^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$
```

This enhanced version gives you complete control over which license plate formats are saved, ensuring high-quality data collection!
