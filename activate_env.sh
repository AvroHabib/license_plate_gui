#!/bin/bash
# License Plate GUI Virtual Environment Activation Script

echo "Activating virtual environment for License Plate GUI..."
cd /home/avrohabib/license_plate_gui
source venv/bin/activate
echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo ""
echo "You can now run your license plate detection applications."
echo "To deactivate the environment, simply type: deactivate"
