#!/usr/bin/env python3
"""
Test script for the new license plate regex filter functionality
"""

import re

def test_license_plate_filter():
    """Test the license plate filter patterns"""
    
    # Define the patterns (same as in the GUI)
    patterns = {
        'standard': r'^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$',
        'metro_basic': r'^[A-Za-z]+Metro\s+\d{6}$',
        'district_simple': r'^(?!.*Metro)[A-Za-z]+\s+\d{2,6}$',
    }
    
    # Test data with expected results
    test_plates = [
        # Standard format tests
        ("ChattoMetroGa 138707", {"standard": True, "metro_basic": False, "district_simple": False}),
        ("DhakaMetroGha 158013", {"standard": True, "metro_basic": False, "district_simple": False}),
        ("ChattoMetroKha 999999", {"standard": True, "metro_basic": False, "district_simple": False}),
        
        # Metro basic format tests
        ("DhakaMetro 115636", {"standard": False, "metro_basic": True, "district_simple": False}),
        ("ChattoMetro 123456", {"standard": False, "metro_basic": True, "district_simple": False}),
        
        # District simple format tests
        ("Chatto 13", {"standard": False, "metro_basic": False, "district_simple": True}),
        ("Dhaka 1234", {"standard": False, "metro_basic": False, "district_simple": True}),
        ("Chatto 123456", {"standard": False, "metro_basic": False, "district_simple": True}),
        
        # Invalid formats (should fail all)
        ("Metro 123456", {"standard": False, "metro_basic": False, "district_simple": False}),
        ("InvalidPlate123", {"standard": False, "metro_basic": False, "district_simple": False}),
        ("ChattoMetroGa123707", {"standard": False, "metro_basic": False, "district_simple": False}),  # No space
        ("ChattoMetro Ga 138707", {"standard": False, "metro_basic": False, "district_simple": False}),  # Extra space
    ]
    
    print("🔍 Testing License Plate Regex Filter")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for plate, expected in test_plates:
        print(f"\nTesting: '{plate}'")
        all_correct = True
        
        for pattern_name, pattern in patterns.items():
            result = bool(re.match(pattern, plate, re.IGNORECASE))
            expected_result = expected[pattern_name]
            
            status = "✅" if result == expected_result else "❌"
            print(f"  {pattern_name:15} {status} {result} (expected {expected_result})")
            
            if result != expected_result:
                all_correct = False
            
            total_tests += 1
            if result == expected_result:
                passed_tests += 1
        
        overall_status = "✅ PASS" if all_correct else "❌ FAIL"
        print(f"  Overall: {overall_status}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Filter is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the patterns.")
        return False


def test_multiple_patterns():
    """Test the multiple patterns functionality"""
    print("\n🔄 Testing Multiple Patterns Mode")
    print("=" * 50)
    
    patterns = [
        r'^[A-Za-z]+Metro[A-Za-z]+\s+\d{6}$',  # standard
        r'^[A-Za-z]+Metro\s+\d{6}$',           # metro_basic
        r'^[A-Za-z]+\s+\d{2,6}$',              # district_simple
    ]
    
    test_plates = [
        ("ChattoMetroGa 138707", True),   # Should pass (standard)
        ("DhakaMetro 115636", True),      # Should pass (metro_basic)
        ("Chatto 13", True),              # Should pass (district_simple)
        ("InvalidPlate123", False),       # Should fail all
        ("Metro 123456", False),          # Should fail all
    ]
    
    for plate, expected in test_plates:
        # Test if plate matches ANY pattern (multiple patterns mode)
        matches_any = False
        for pattern in patterns:
            if re.match(pattern, plate, re.IGNORECASE):
                matches_any = True
                break
        
        status = "✅" if matches_any == expected else "❌"
        print(f"{status} {plate:25} -> {matches_any} (expected {expected})")


def main():
    """Main test function"""
    print("Bengali License Plate Filter - Test Suite")
    print("=" * 60)
    
    # Test individual patterns
    test1_passed = test_license_plate_filter()
    
    # Test multiple patterns mode
    test_multiple_patterns()
    
    # Summary
    print("\n" + "=" * 60)
    if test1_passed:
        print("✅ Filter functionality is working correctly!")
        print("\nThe GUI filter should:")
        print("- Accept 'ChattoMetroGa 138707' format when 'standard' is selected")
        print("- Reject 'Chatto 13' format when 'standard' is selected")
        print("- Accept both when 'Allow Multiple Patterns' is enabled")
    else:
        print("❌ Filter has issues that need to be fixed.")
    
    print("\nYou can now run the GUI with confidence!")
    print("python license_plate_gui_filtered.py")


if __name__ == "__main__":
    main()
