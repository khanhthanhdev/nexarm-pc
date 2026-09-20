"""3D Arm Visualization — full STL, background loading with spinner."""
import os
import math
import struct
import struct as _struct
import threading
import numpy as np
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton,
    QGroupBox, QGridLayout, QStackedWidget, QDoubleSpinBox, QSpinBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal
from PyQt5.QtGui import QMatrix4x4, QPainter, QColor, QPen, QPixmap

try:
    import pyqtgraph.opengl as gl
except ImportError:
    gl = None

from nexarm_qt.ui.urdf_parser import parse_urdf, joint_transform, make_transform, axis_angle_matrix
from nexarm_qt.constants import CMD_SET_SINGLE_MOTOR, CMD_COORDINATE_SET
from nexarm_qt.translations import STRINGS
from nexarm_qt.styles import S

SCALE = 1000
SKIP_LINKS = {'camera_link'}
LINK_COLORS = [
    (0.55, 0.55, 0.6, 1.0),
    (0.3, 0.6, 0.95, 1.0),
    (0.3, 0.8, 0.45, 1.0),
    (0.95, 0.6, 0.25, 1.0),
    (0.75, 0.35, 0.8, 1.0),
    (0.8, 0.6, 0.1, 1.0),
    (0.55, 0.1, 0.55, 1.0),
    (0.02, 0.02, 0.02, 1.0),
    (0.02, 0.02, 0.02, 1.0),
    (0.02, 0.02, 0.02, 1.0)
]


def load_stl_full(path):
    """Load ALL faces from binary STL using numpy bulk read."""
    if not os.path.exists(path):
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int32)
    with open(path, "rb") as f:
        f.read(80)
        n_bytes = f.read(4)
        if len(n_bytes) < 4:
            return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int32)
        n = _struct.unpack("<I", n_bytes)[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8)
    if len(raw) < n * 50:
        n = len(raw) // 50
    if n == 0:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int32)
    raw = raw[:n * 50].reshape(n, 50)
    vb = raw[:, 12:48].copy()
    verts = vb.view(np.float32).reshape(n, 3, 3) * SCALE
    verts = verts.reshape(-1, 3)
    faces = np.arange(n * 3, dtype=np.int32).reshape(n, 3)
    return verts, faces


def np44_to_qmatrix(T):
    return QMatrix4x4(*T.flatten().tolist())


class SpinnerWidget(QWidget):
    """Rotating spinner shown while loading."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._progress = ""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self.setMinimumSize(200, 200)

    def start(self):
        self._timer.start(30)

    def stop(self):
        self._timer.stop()

    def set_progress(self, text):
        self._progress = text

    def _rotate(self):
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(30, 30, 40))
        cx = self.width() // 2
        cy = self.height() // 2
        r = min(cx, cy) - 40
        if r < 20:
            r = 20
        pen = QPen(QColor(250, 143, 1), 4)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.translate(cx, cy)
        p.rotate(self._angle)
        p.drawArc(-r, -r, r * 2, r * 2, 0, 4320)
        p.resetTransform()
        p.setPen(QColor(180, 180, 180))
        font = p.font()
        font.setPixelSize(14)
        p.setFont(font)
        text = self._progress if self._progress else STRINGS.get('zh', {}).get('lbl_loading_3d', 'Loading 3D models...')
        p.drawText(self.rect(), Qt.AlignCenter, text)
        p.end()


class Arm3DWidget(QWidget):
    """3D arm visualization with full STL, background loading."""
    _meshes_ready = pyqtSignal(list)
    _load_progress = pyqtSignal(str)

    JOINT_LABELS = [
        'J1 Base',
        'J2 Shoulder',
        'J3 Elbow',
        'J4 Wrist',
        'J5 Rotate',
        'J6 Claw'
    ]

    SERVO_CENTER = [2048, 2048, 2048, 2048, 1198, 1238]
    SERVO_RATIO = [0.087890625, 0.087890625, 0.087890625, 0.087890625, 0.05859375, 0.05859375]
    SERVO_DIR = [1, 1, 1, 1, 1, 1]
    URDF_DIR = [1, 1, 1, 1, 1, 1]

    def __init__(self, comm_manager=None, lang='zh', parent=None):
        super().__init__(parent)
        self.comm_manager = comm_manager
        self.lang = lang
        self.links = []
        self.joints = []
        self.joint_angles = [0.0] * 6
        self.mesh_items = {}
        self.coord_inputs = {}

        self._build_ui()
        self._start_bg_load()

        if self.comm_manager:
            self.comm_manager.coord_updated.connect(self._on_coord_updated)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.spinner = SpinnerWidget()
        self.stack.addWidget(self.spinner)

        if gl:
            self.view = gl.GLViewWidget()
            self.view.setBackgroundColor(QColor(30, 30, 40))
            self.view.setCameraPosition(distance=1500, elevation=30, azimuth=45)
            grid = gl.GLGridItem()
            grid.scale(50, 50, 1)
            self.view.addItem(grid)
            axis = gl.GLAxisItem()
            axis.setSize(x=200, y=200, z=200)
            self.view.addItem(axis)
            self.stack.addWidget(self.view)
        else:
            lbl = QLabel("PyOpenGL / pyqtgraph not installed")
            self.stack.addWidget(lbl)

        layout.addWidget(self.stack)

    def _start_bg_load(self):
        self.spinner.start()
        threading.Thread(target=self._load_meshes_worker, daemon=True).start()
        self._meshes_ready.connect(self._on_meshes_ready)

    def _load_meshes_worker(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        urdf_path = os.path.join(base_dir, "ui", "nexarm.urdf")
        stl_dir = os.path.join(base_dir, "STL")

        if not os.path.exists(urdf_path):
            urdf_path = os.path.join(base_dir, "..", "ui", "nexarm.urdf")
            stl_dir = os.path.join(base_dir, "..", "STL")

        mesh_data_list = []
        if os.path.exists(urdf_path):
            try:
                self.links, self.joints = parse_urdf(urdf_path, stl_dir)
                for i, link in enumerate(self.links):
                    mesh_p = link.get("mesh_path")
                    if mesh_p and os.path.exists(mesh_p):
                        verts, faces = load_stl_full(mesh_p)
                        color = LINK_COLORS[i % len(LINK_COLORS)]
                        mesh_data_list.append((link["name"], verts, faces, color))
            except Exception as e:
                print(f"URDF load error: {e}")

        self._meshes_ready.emit(mesh_data_list)

    def _on_meshes_ready(self, mesh_data_list):
        self.spinner.stop()
        if gl and hasattr(self, 'view'):
            for name, verts, faces, color in mesh_data_list:
                if len(verts) > 0 and len(faces) > 0:
                    item = gl.GLMeshItem(vertexes=verts, faces=faces, smooth=True, color=color, shader='shaded')
                    self.mesh_items[name] = item
                    self.view.addItem(item)
            self.stack.setCurrentIndex(1)
            self._update_model()
        else:
            self.stack.setCurrentIndex(1)

    def _servo_to_angles(self, servo_vals):
        for i in range(min(6, len(servo_vals))):
            deg = (servo_vals[i] - self.SERVO_CENTER[i]) * self.SERVO_RATIO[i] * self.SERVO_DIR[i] * self.URDF_DIR[i]
            self.joint_angles[i] = math.radians(deg)

    def _compute_link_transforms(self):
        transforms = {}
        T = np.eye(4)
        for i, joint in enumerate(self.joints):
            angle = self.joint_angles[i] if i < len(self.joint_angles) else 0.0
            T_joint = joint_transform(joint, angle)
            T = T @ T_joint
            transforms[joint["child"]] = T
        return transforms

    def _update_model(self):
        if not self.mesh_items:
            return
        transforms = self._compute_link_transforms()
        for name, item in self.mesh_items.items():
            if name in transforms:
                item.setTransform(np44_to_qmatrix(transforms[name]))

    def _slider_moved(self, idx, val_deg):
        if idx < len(self.joint_angles):
            self.joint_angles[idx] = math.radians(val_deg)
            self._update_model()

    def _send_joint(self, idx, angle_deg):
        if self.comm_manager:
            self.comm_manager.send_sys(CMD_SET_SINGLE_MOTOR, [idx + 1, int(angle_deg)])

    def _send_coordinate(self):
        pass

    def eventFilter(self, obj, event):
        return super().eventFilter(obj, event)

    def _on_coord_updated(self, x, y, z, pitch, roll, claw, servo_angles):
        if servo_angles and len(servo_angles) >= 6:
            self._servo_to_angles(servo_angles)
            self._update_model()

    def update_coord_inputs(self, x, y, z, pitch, roll, claw):
        pass

    def _home_all(self):
        self.joint_angles = [0.0] * 6
        self._update_model()

    def update_language(self, lang):
        self.lang = lang
