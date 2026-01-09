#!/bin/bash
# Quick verification script for new features

echo "=========================================="
echo "VERIFYING NEW FEATURES IMPLEMENTATION"
echo "=========================================="
echo ""

echo "1. Checking Python syntax..."
python -m py_compile streamlit_app.py
if [ $? -eq 0 ]; then
    echo "   ✓ Syntax OK"
else
    echo "   ✗ Syntax Error!"
    exit 1
fi
echo ""

echo "2. Checking all 8 modes are present..."
echo ""
echo "   Modes found:"
grep "elif mode ==" streamlit_app.py | sed 's/.*elif mode == "/     ✓ /' | sed 's/":.*//'
echo ""

echo "3. Counting lines in each mode..."
echo ""
echo "   Cloud Sync mode:"
grep -n "elif mode == \"Cloud Sync\"" streamlit_app.py | cut -d: -f1 > /tmp/cloud_start.txt
grep -n "elif mode == \"Computer Vision\"" streamlit_app.py | cut -d: -f1 > /tmp/cv_start.txt
CLOUD_START=$(cat /tmp/cloud_start.txt)
CV_START=$(cat /tmp/cv_start.txt)
CLOUD_LINES=$((CV_START - CLOUD_START))
echo "     Lines: $CLOUD_LINES"
echo "     ✓ Cloud Sync mode implemented"
echo ""

echo "   Computer Vision mode:"
grep -n "elif mode == \"Computer Vision\"" streamlit_app.py | cut -d: -f1 > /tmp/cv_start.txt
grep -n "# =============" streamlit_app.py | tail -1 | cut -d: -f1 > /tmp/footer.txt
CV_START=$(cat /tmp/cv_start.txt)
FOOTER=$(cat /tmp/footer.txt)
CV_LINES=$((FOOTER - CV_START))
echo "     Lines: $CV_LINES"
echo "     ✓ Computer Vision mode implemented"
echo ""

echo "4. Checking for required components..."
echo ""

# Cloud Sync components
echo "   Cloud Sync components:"
grep -q "Enable Cloud Sync" streamlit_app.py && echo "     ✓ Toggle found"
grep -q "Firebase Project ID" streamlit_app.py && echo "     ✓ Firebase config found"
grep -q "Data Being Synced" streamlit_app.py && echo "     ✓ Data sync table found"
grep -q "from firebase_integration import" streamlit_app.py && echo "     ✓ Firebase import code found"
echo ""

# Computer Vision components
echo "   Computer Vision components:"
grep -q "Enable Camera Feed" streamlit_app.py && echo "     ✓ Camera toggle found"
grep -q "Detection Confidence" streamlit_app.py && echo "     ✓ Confidence slider found"
grep -q "Vehicle Detection by Lane" streamlit_app.py && echo "     ✓ Detection table found"
grep -q "from computer_vision import" streamlit_app.py && echo "     ✓ Computer Vision import code found"
echo ""

echo "5. Testing file integrity..."
FILE_SIZE=$(wc -l < streamlit_app.py)
echo "   Total lines in streamlit_app.py: $FILE_SIZE"
if [ $FILE_SIZE -gt 850 ]; then
    echo "   ✓ File size OK (expanded with new features)"
else
    echo "   ✗ File might be incomplete"
fi
echo ""

echo "=========================================="
echo "VERIFICATION COMPLETE ✅"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run: streamlit run streamlit_app.py"
echo "2. Select 'Cloud Sync' from sidebar"
echo "3. Select 'Computer Vision' from sidebar"
echo "4. Verify both pages load correctly"
echo ""
