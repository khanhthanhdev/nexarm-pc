# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

added_files = [
    ('STL', 'STL'),
    ('ui/nexarm.urdf', 'ui'),
    ('nexarm_icon.png', '.'),
    ('coord_axes.png', '.'),
    ('0.842.png', '.')
]

hidden_imports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtOpenGL',
    'pyqtgraph',
    'pyqtgraph.opengl',
    'OpenGL',
    'OpenGL.GL',
    'OpenGL.arrays.numpymodule',
    'serial',
    'serial.tools.list_ports',
    'numpy',
    'PIL',
    'cv2',
    'nexarm_qt',
    'nexarm_qt.constants',
    'nexarm_qt.comm_manager',
    'nexarm_qt.styles',
    'nexarm_qt.translations',
    'nexarm_qt.ui',
    'nexarm_qt.ui.main_window',
    'nexarm_qt.ui.coord_tab',
    'nexarm_qt.ui.servo_tab',
    'nexarm_qt.ui.servo_advanced_tab',
    'nexarm_qt.ui.teach_tab',
    'nexarm_qt.ui.ai_tab',
    'nexarm_qt.ui.ai_calibration_widget',
    'nexarm_qt.ui.peripheral_tab',
    'nexarm_qt.ui.system_tab',
    'nexarm_qt.ui.arm_3d_widget',
    'nexarm_qt.ui.arm_3d_window',
    'nexarm_qt.ui.dpad_widget',
    'nexarm_qt.ui.log_widget',
    'nexarm_qt.ui.urdf_parser'
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NexArm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='nexarm_icon.png' if sys.platform != 'darwin' else None,
)

# On macOS, generate a .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='NexArm.app',
        icon='nexarm_icon.png',
        bundle_identifier='com.nexarm.controller',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'NSRequiresAquaSystemAppearance': 'False'
        }
    )
