# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.14.6 | packaged by Anaconda, Inc. | (main, Jun 18 2026, 21:18:42) [MSC v.1942 64 bit (AMD64)]
# Embedded file name: nexarm_qt\ui\dpad_widget.py
"""
圆形方向盘控件 — 类似游戏手柄的扇形按钮
4dir: 4方向圆盘（履带）
mecanum: 4方向圆盘 + 左右平移扇形（麦轮），支持多键同时按下
"""
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QFont, QPen, QBrush
import math

class DPad(QWidget):
    __doc__ = "圆形方向盘控件\n\n    mode='4dir': ↑↓←→ (履带)\n    mode='6dir': 中间WSAD + 两侧QE平移 (麦轮)，支持同时按下\n    "
    direction_pressed = pyqtSignal(str)
    direction_released = pyqtSignal(str)
    stop_clicked = pyqtSignal()

    def __init__(self, mode='4dir', parent=None, lang='zh'):
        super().__init__(parent)
        self.mode = mode
        from nexarm_qt.translations import STRINGS
        S = STRINGS.get(lang, STRINGS["zh"])
        fwd = S.get("lbl_fwd", "Fwd")
        back = S.get("lbl_back", "Back")
        left = S.get("lbl_left", "Left")
        right = S.get("lbl_right", "Right")
        self._stop_label = S.get("lbl_stop", "Stop")
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)
        self._active_set = set()
        self._stop_flash = False
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._clear_flash)
        if mode == "6dir":
            self._dirs = [{'name':"up",  'label':f"W\n{fwd}",  'key':Qt.Key_W,  'angle':90,  'span':90},
             {'name':"right", 
              'label':f"D\n{right}",  'key':Qt.Key_D,  'angle':0,  'span':90},
             {'name':"down", 
              'label':f"S\n{back}",  'key':Qt.Key_S,  'angle':-90,  'span':90},
             {'name':"left", 
              'label':f"A\n{left}",  'key':Qt.Key_A,  'angle':180,  'span':90}]
            self._strafe = [
             {'name':"left_strafe", 
              'label':f"Q\n{left}",  'key':Qt.Key_Q,  'side':"left"},
             {'name':"right_strafe", 
              'label':f"E\n{right}",  'key':Qt.Key_E,  'side':"right"}]
        else:
            self._dirs = [{'name':"up",  'label':f"↑\n{fwd}",  'key':Qt.Key_Up,  'angle':90,  'span':90},
             {'name':"right", 
              'label':f"→\n{right}",  'key':Qt.Key_Right,  'angle':0,  'span':90},
             {'name':"down", 
              'label':f"↓\n{back}",  'key':Qt.Key_Down,  'angle':-90,  'span':90},
             {'name':"left", 
              'label':f"←\n{left}",  'key':Qt.Key_Left,  'angle':180,  'span':90}]
            self._strafe = []

    def _clear_flash(self):
        self._stop_flash = False
        self.update()

    def flash_stop(self):
        self._stop_flash = True
        self.update()
        self._flash_timer.start(300)

    def _geometry(self):
        """返回绘制所需的几何参数"""
        w, h = self.width(), self.height()
        if self.mode == "6dir":
            pad = w * 0.18
            cx = w / 2
            cy = h / 2
            side = min(w - pad * 2, h)
            outer_r = side * 0.42
            inner_r = side * 0.16
            strafe_w = pad * 0.85
        else:
            cx, cy = w / 2, h / 2
            side = min(w, h)
            outer_r = side * 0.45
            inner_r = side * 0.18
            pad = 0
            strafe_w = 0
        return (
         cx, cy, outer_r, inner_r, pad, strafe_w)

    def _strafe_path(self, side):
        """构建左/右平移 — 完整扇形，和圆盘的A/D之间留间距"""
        cx, cy, outer_r, inner_r, pad, strafe_w = self._geometry()
        arc_inner = outer_r + outer_r * 0.22
        arc_outer = arc_inner + strafe_w * 0.55
        span_deg = 50
        gap = 10
        if side == "left":
            center_angle = 180
        else:
            center_angle = 0
        start = center_angle - span_deg / 2
        path = QPainterPath()
        outer_rect = QRectF(cx - arc_outer, cy - arc_outer, arc_outer * 2, arc_outer * 2)
        inner_rect = QRectF(cx - arc_inner, cy - arc_inner, arc_inner * 2, arc_inner * 2)
        path.arcMoveTo(outer_rect, start)
        path.arcTo(outer_rect, start, span_deg)
        path.arcTo(inner_rect, start + span_deg, -span_deg)
        path.closeSubpath()
        mid_angle = math.radians(center_angle)
        text_r = (arc_inner + arc_outer) / 2
        tx = cx + text_r * math.cos(mid_angle)
        ty = cy - text_r * math.sin(mid_angle)
        text_rect = QRectF(tx - 25, ty - 15, 50, 30)
        return (
         path, text_rect)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy, outer_r, inner_r, pad, strafe_w = self._geometry()
        gap = 2
        color_normal = QColor(52, 54, 69)
        color_active = QColor(250, 143, 1)
        color_border = QColor(74, 77, 94)
        color_text = QColor(255, 255, 255)
        color_stop_normal = QColor(74, 77, 94)
        for d in self._dirs:
            is_active = d["name"] in self._active_set
            fill = color_active if is_active else color_normal
            start_angle = d["angle"] - d["span"] / 2 + gap / 2
            sweep = d["span"] - gap
            path = QPainterPath()
            outer_rect = QRectF(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
            inner_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)
            path.arcMoveTo(outer_rect, start_angle)
            path.arcTo(outer_rect, start_angle, sweep)
            path.arcTo(inner_rect, start_angle + sweep, -sweep)
            path.closeSubpath()
            p.setPen(QPen(color_border, 1.5))
            p.setBrush(QBrush(fill))
            p.drawPath(path)
            mid_angle = math.radians(d["angle"])
            text_r = (outer_r + inner_r) / 2
            tx = cx + text_r * math.cos(mid_angle)
            ty = cy - text_r * math.sin(mid_angle)
            font = QFont()
            font.setPointSize(8)
            font.setBold(is_active)
            p.setFont(font)
            p.setPen(color_active if is_active else color_text)
            text_rect = QRectF(tx - 30, ty - 15, 60, 30)
            p.drawText(text_rect, Qt.AlignCenter, d["label"])
        else:
            for s in self._strafe:
                is_active = s["name"] in self._active_set
                fill = color_active if is_active else color_normal
                path, rect = self._strafe_path(s["side"])
                p.setPen(QPen(color_border, 1.5))
                p.setBrush(QBrush(fill))
                p.drawPath(path)
                font = QFont()
                font.setPointSize(8)
                font.setBold(is_active)
                p.setFont(font)
                p.setPen(color_active if is_active else color_text)
                p.drawText(rect, Qt.AlignCenter, s["label"])
            else:
                stop_color = color_active if self._stop_flash else color_stop_normal
                p.setPen(QPen(color_border, 1.5))
                p.setBrush(QBrush(stop_color))
                p.drawEllipse(QPointF(cx, cy), inner_r - 3, inner_r - 3)
                font = QFont()
                font.setPointSize(9)
                font.setBold(True)
                p.setFont(font)
                p.setPen(color_active if self._stop_flash else color_text)
                stop_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)
                p.drawText(stop_rect, Qt.AlignCenter, self._stop_label)
                p.end()

    def mousePressEvent(self, event):
        name = self._hit_test(event.pos())
        if name == "stop":
            self.stop_clicked.emit()
            self.flash_stop()
        else:
            if name:
                self._active_set.add(name)
                self.update()
                self.direction_pressed.emit(name)

    def mouseReleaseEvent(self, event):
        released = set()
        for name in list(self._active_set):
            released.add(name)
        else:
            for name in released:
                if name in self._active_set:
                    self._active_set.discard(name)
                    self.direction_released.emit(name)
            else:
                self.update()

    def _hit_test(self, pos):
        cx, cy, outer_r, inner_r, pad, strafe_w = self._geometry()
        dx = pos.x() - cx
        dy = -(pos.y() - cy)
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < inner_r - 3:
            return "stop"
        for s in self._strafe:
            path, rect = self._strafe_path(s["side"])
            if path.contains(QPointF(pos.x(), pos.y())):
                return s["name"]
            if dist > outer_r:
                return
            angle = math.degrees(math.atan2(dy, dx))
            for d in self._dirs:
                half = d["span"] / 2
                center = d["angle"]
                diff = (angle - center + 180) % 360 - 180
                if abs(diff) < half:
                    return d["name"]
                return

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        all_dirs = self._dirs + self._strafe
        for d in all_dirs:
            if event.key() == d["key"]:
                if d["name"] not in self._active_set:
                    self._active_set.add(d["name"])
                    self.update()
                return
            if event.key() == Qt.Key_Space:
                self.stop_clicked.emit()
                self.flash_stop()
                return
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        all_dirs = self._dirs + self._strafe
        for d in all_dirs:
            if event.key() == d["key"]:
                if d["name"] in self._active_set:
                    self._active_set.discard(d["name"])
                    self.update()
                    self.direction_released.emit(d["name"])
                return
        super().keyReleaseEvent(event)

    def update_language(self, lang):
        from nexarm_qt.translations import STRINGS
        S = STRINGS[lang]
        fwd = S.get("lbl_fwd", "Fwd")
        back = S.get("lbl_back", "Back")
        left = S.get("lbl_left", "Left")
        right = S.get("lbl_right", "Right")
        self._stop_label = S.get("lbl_stop", "Stop")
        key_map = {
            'up': fwd,
            'down': back,
            'left': left,
            'right': right
        }
        for d in self._dirs:
            key_char = d["label"].split("\n")[0]
            if d["name"] in key_map:
                d["label"] = f'{key_char}\n{key_map[d["name"]]}'
        else:
            if hasattr(self, "_strafe"):
                strafe_map = {'left_strafe':(S.get)("lbl_left", "Left"),  'right_strafe':(S.get)("lbl_right", "Right")}
                for d in self._strafe:
                    key_char = d["label"].split("\n")[0]
                    if d["name"] in strafe_map:
                        d["label"] = f'{key_char}\n{strafe_map[d["name"]]}'

            self.update()
