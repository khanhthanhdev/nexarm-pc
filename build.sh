#!/usr/bin/env bash
set -e

echo "=== Building NexArm for $(uname -s) ($(uname -m)) ==="

# Check Python version
python3 --version

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install system dependencies on Ubuntu / Debian
if command -v apt-get &> /dev/null; then
    echo "Ensuring required OpenGL & Qt system libraries for Ubuntu..."
    sudo apt-get update
    # Ubuntu 24.04 compatible package list (replaces deprecated libgl1-mesa-glx with libgl1/libglx-mesa0)
    sudo apt-get install -y --no-install-recommends \
        libgl1 \
        libglx-mesa0 \
        libgl1-mesa-dri \
        libegl1 \
        libxcb-cursor0 \
        libxcb-xinerama0 \
        libxkbcommon-x11-0 \
        libpulse0
fi

# Install Python requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run PyInstaller
echo "Compiling application with PyInstaller..."
pyinstaller --clean nexarm.spec

echo "=== Build Complete! ==="
if [ "$(uname -s)" = "Darwin" ]; then
    echo "Artifact: dist/NexArm.app"
else
    echo "Artifact: dist/NexArm"
    # Package into tar.gz
    tar -czvf dist/NexArm-Ubuntu-24.04-x86_64.tar.gz -C dist NexArm
    echo "Release Archive: dist/NexArm-Ubuntu-24.04-x86_64.tar.gz"
fi
