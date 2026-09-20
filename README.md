# NexArm Controller (Cross-Platform)

Cross-platform desktop controller for the NexArm robotic arm, built with PyQt5, PyOpenGL, and pyqtgraph.

---

## 🚀 Running on Ubuntu 24.04 LTS

### 1. Install System Dependencies
Ubuntu 24.04 requires the modern Mesa OpenGL and XCB/Qt libraries:
```bash
sudo apt update
sudo apt install -y --no-install-recommends \
    python3-pip python3-venv \
    libgl1 libglx-mesa0 libgl1-mesa-dri libegl1 \
    libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 \
    libpulse0
```

### 2. Grant USB Serial Permissions
To communicate with the robot arm via USB UART:
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in for changes to take effect
```

### 3. Run Directly with Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### 4. Build Standalone Linux Executable Locally
```bash
chmod +x build.sh
./build.sh
```
The compiled binary will be in `dist/NexArm` and archived in `dist/NexArm-Ubuntu-24.04-x86_64.tar.gz`.

---

## 📦 Automated GitHub Release for Ubuntu 24.04

The repository includes a GitHub Actions workflow at `.github/workflows/release.yml`.

### How to Trigger an Official Release:
1. Push your commits to GitHub:
   ```bash
   git add .
   git commit -m "Prepare release"
   git push origin main
   ```
2. Tag a new release version and push the tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions will automatically:
   - Spin up a clean **Ubuntu 24.04 LTS** runner.
   - Install all system and Python dependencies.
   - Compile the standalone binary with PyInstaller.
   - Package `NexArm`, `STL/` 3D meshes, and `ui/` resources into `NexArm-Ubuntu-24.04-x86_64.tar.gz`.
   - Publish a new **GitHub Release** with the downloadable archive attached!
