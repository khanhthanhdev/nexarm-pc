# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.14.6 | packaged by Anaconda, Inc. | (main, Jun 18 2026, 21:18:42) [MSC v.1942 64 bit (AMD64)]
# Embedded file name: nexarm_qt\main.py
import sys, os, traceback
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from nexarm_qt.styles import DARK_THEME

def excepthook(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("Uncaught exception:", error_msg)
    try:
        with open("crash_log.txt", "w") as f:
            f.write(error_msg)
    except:
        pass
    else:
        if QApplication.instance():
            QMessageBox.critical(None, "Application Crash", f"An unexpected error occurred:\n{exc_value}\n\nSee crash_log.txt for details.")
        sys.exit(1)


sys.excepthook = excepthook
from nexarm_qt.ui.main_window import MainWindow
if __name__ == "__main__":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_THEME)
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        try:
            excepthook(type(e), e, e.__traceback__)
        finally:
            e = None
            del e
