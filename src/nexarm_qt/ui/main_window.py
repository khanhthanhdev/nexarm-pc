# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.14.6 | packaged by Anaconda, Inc. | (main, Jun 18 2026, 21:18:42) [MSC v.1942 64 bit (AMD64)]
# Embedded file name: nexarm_qt\ui\main_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QComboBox, QPushButton, QGroupBox, QFrame, QListWidget, QStackedWidget, QListView, QLineEdit, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSettings
from nexarm_qt.comm_manager import CommManager
from nexarm_qt.constants import CMD_GET_CUR_COORDS
from nexarm_qt.ui.log_widget import LogWidget
from nexarm_qt.ui.servo_tab import ServoTab
from nexarm_qt.ui.coord_tab import CoordTab
from nexarm_qt.ui.peripheral_tab import PeripheralTab
from nexarm_qt.ui.system_tab import SystemTab
from nexarm_qt.ui.ai_tab import AITab
from nexarm_qt.ui.servo_advanced_tab import ServoAdvancedTab
from nexarm_qt.ui.teach_tab import TeachTab
from nexarm_qt.translations import STRINGS

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.lang = "zh"
        self.settings = QSettings("NexArm", "NexArmQt")
        self.setWindowTitle(STRINGS[self.lang]["window_title"])
        self.setMinimumSize(800, 600)
        from PyQt5.QtWidgets import QDesktopWidget
        avail = QDesktopWidget().availableGeometry()
        w = int(avail.width() * 0.9)
        h = int(avail.height() * 0.9)
        self.resize(w, h)
        import sys, os
        icon_path = os.path.join(sys._MEIPASS, "nexarm_icon.png") if hasattr(sys, "_MEIPASS") else "nexarm_icon.png"
        self.setWindowIcon(QIcon(icon_path))
        self._dpi_scale = self.logicalDpiX() / 96.0
        self.comm_manager = CommManager()
        self.setup_ui()
        self.connect_signals()
        self.refresh_ports()

    def _s(self, px):
        return int(px)

    def update_language(self):
        self.setWindowTitle(STRINGS[self.lang]["window_title"])
        self.nav_list.item(0).setText(STRINGS[self.lang]["tab_servo"])
        self.nav_list.item(1).setText(STRINGS[self.lang]["tab_coord"])
        self.nav_list.item(2).setText(STRINGS[self.lang]["tab_peripheral"])
        self.nav_list.item(3).setText(STRINGS[self.lang]["tab_system"])
        self.nav_list.item(4).setText(STRINGS[self.lang]["tab_ai"])
        self.nav_list.item(5).setText(STRINGS[self.lang]["tab_servo_adv"])
        self.nav_list.item(6).setText(STRINGS[self.lang].get("tab_teach", "Teach Edit"))
        self.header_lbl.setText(self.nav_list.currentItem().text())
        self.update_connection_status(self.comm_manager.is_connected, "")
        self.lbl_method.setText(STRINGS[self.lang].get("comm_method", "Connection:"))
        self.cb_method.setItemText(0, STRINGS[self.lang].get("method_serial", "Serial"))
        self.cb_method.setItemText(1, STRINGS[self.lang].get("method_wifi", "WiFi"))
        self.lbl_ssid.setText(STRINGS[self.lang].get("ssid", "WiFi:"))
        self.lbl_pwd.setText(STRINGS[self.lang].get("password", "Pwd:"))
        self.btn_scan.setText(STRINGS[self.lang].get("search", "Search"))
        self.chk_show_pwd.setText(STRINGS[self.lang].get("chk_show_pwd", "Show"))
        if hasattr(self, "lbl_port"):
            self.lbl_port.setText(STRINGS[self.lang].get("port", "Port:"))
        if hasattr(self, "btn_refresh"):
            self.btn_refresh.setText(STRINGS[self.lang].get("refresh", "Refresh"))
        if hasattr(self, "lbl_baud"):
            self.lbl_baud.setText(STRINGS[self.lang].get("lbl_baud_rate", "Baud Rate:"))
        self.btn_lang.setText("English" if self.lang == "zh" else "中文")
        self.lbl_off.setText(STRINGS[self.lang].get("lbl_toggle_off", "OFF"))
        self.lbl_on.setText(STRINGS[self.lang].get("lbl_toggle_on", "ON"))
        self.tab_servo.update_language(self.lang)
        self.tab_coord.update_language(self.lang)
        self.tab_peripheral.update_language(self.lang)
        self.tab_system.update_language(self.lang)
        self.tab_ai.update_language(self.lang)
        self.tab_servo_adv.update_language(self.lang)
        self.tab_teach.update_language(self.lang)
        self.log_widget.update_language(self.lang)

    def toggle_language(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.btn_lang.setText("English" if self.lang == "zh" else "中文")
        self.update_language()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(self._s(220))
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 5, 0, 5)
        logo_label = QLabel()
        import sys, os
        icon_path2 = os.path.join(sys._MEIPASS, "nexarm_icon.png") if hasattr(sys, "_MEIPASS") else "nexarm_icon.png"
        logo_pix = QIcon(icon_path2).pixmap(90, 90)
        logo_label.setPixmap(logo_pix)
        logo_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(logo_label)
        sidebar_layout.addWidget(title_container)
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("NavList")
        self.nav_list.addItems([
         STRINGS[self.lang]["tab_servo"],
         STRINGS[self.lang]["tab_coord"],
         STRINGS[self.lang]["tab_peripheral"],
         STRINGS[self.lang]["tab_system"],
         STRINGS[self.lang]["tab_ai"],
         STRINGS[self.lang]["tab_servo_adv"],
         STRINGS[self.lang].get("tab_teach", "示教编辑")])
        self.nav_list.setSpacing(10)
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.on_nav_changed)
        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setMinimumHeight(self._s(450))
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        comm_container = QWidget()
        comm_container.setStyleSheet("\n            QWidget { background-color: transparent; }\n            QComboBox, QLineEdit {\n                background-color: transparent;\n                border: 1px solid #666666;\n                border-radius: 4px;\n                color: #FFFFFF;\n                padding: 4px;\n                min-height: 15pt;\n            }\n            QComboBox:hover, QLineEdit:hover {\n                border: 1px solid #999999;\n            }\n            QComboBox:focus, QLineEdit:focus, QComboBox:on {\n                border: 1px solid #FA8F01;\n            }\n            QComboBox::drop-down { border: none; width: 20px; }\n        ")
        comm_layout = QVBoxLayout(comm_container)
        comm_layout.setContentsMargins(25, 15, 25, 6)
        comm_layout.setSpacing(15)
        comm_layout.setContentsMargins(20, 6, 20, 20)
        comm_layout.setSpacing(12)
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #F44336; font-size: 11pt;")
        status_row.addWidget(self.status_dot)
        self.lbl_status = QLabel(STRINGS[self.lang]["status_disconnected"])
        self.lbl_status.setProperty("class", "status-error")
        self.lbl_status.setStyleSheet("QLabel { font-weight: bold; color: #B0BEC5; font-size: 9pt; }")
        status_row.addWidget(self.lbl_status)
        status_row.addStretch()
        comm_layout.addLayout(status_row)
        self.lbl_method = QLabel(STRINGS[self.lang].get("comm_method", "通信方式"))
        self.lbl_method.setProperty("class", "aux-text")
        self.lbl_method.setStyleSheet("color: #78909C;")
        comm_layout.addWidget(self.lbl_method)
        self.cb_method = QComboBox()
        self.cb_method.setView(QListView())
        self.cb_method.addItems([STRINGS[self.lang].get("method_serial", "Serial"), STRINGS[self.lang].get("method_wifi", "WiFi")])
        comm_layout.addWidget(self.cb_method)
        self.stack_comm = QStackedWidget()
        page_serial = QWidget()
        layout_serial = QVBoxLayout(page_serial)
        layout_serial.setContentsMargins(0, 0, 0, 0)
        layout_serial.setSpacing(5)
        lbl_p = QLabel(STRINGS[self.lang]["port"])
        lbl_p.setProperty("class", "aux-text")
        lbl_p.setStyleSheet("color: #78909C;")
        self.lbl_port = lbl_p
        layout_serial.addWidget(lbl_p)
        port_row = QHBoxLayout()
        self.cb_port = QComboBox()
        self.cb_port.setView(QListView())
        port_row.addWidget(self.cb_port, 1)
        self.btn_refresh = QPushButton(STRINGS[self.lang]["refresh"])
        self.btn_refresh.setFixedSize(self._s(60), self._s(35))
        self.btn_refresh.setStyleSheet("\n            QPushButton {\n                background-color: transparent;\n                border: 1px solid rgba(255, 255, 255, 0.2);\n                border-radius: 4px;\n                color: #B0BEC5;\n                font-family: 'Microsoft YaHei';\n                font-size: 9pt;\n                padding: 0px;\n            }\n            QPushButton:hover {\n                border: 1px solid #FA8F01;\n                color: #FFFFFF;\n            }\n        ")
        self.btn_refresh.clicked.connect(self.refresh_ports)
        port_row.addWidget(self.btn_refresh)
        layout_serial.addLayout(port_row)
        lbl_b = QLabel(STRINGS[self.lang].get("lbl_baud_rate", "波特率:"))
        lbl_b.setProperty("class", "aux-text")
        lbl_b.setStyleSheet("color: #78909C;")
        self.lbl_baud = lbl_b
        layout_serial.addWidget(lbl_b)
        self.cb_baud = QComboBox()
        self.cb_baud.setView(QListView())
        self.cb_baud.addItems(['9600', '19200', '38400', '57600', '76800', '115200', '128000', '250000', 
         '500000', '1000000', '2000000'])
        self.cb_baud.setCurrentText("1000000")
        layout_serial.addWidget(self.cb_baud)
        self.stack_comm.addWidget(page_serial)
        page_wifi = QWidget()
        layout_wifi = QVBoxLayout(page_wifi)
        layout_wifi.setContentsMargins(0, 0, 0, 0)
        layout_wifi.setSpacing(10)
        self.lbl_ssid = QLabel(STRINGS[self.lang].get("ssid", "WiFi:"))
        self.lbl_ssid.setProperty("class", "aux-text")
        self.lbl_ssid.setStyleSheet("color: #78909C;")
        layout_wifi.addWidget(self.lbl_ssid)
        ssid_row = QHBoxLayout()
        self.cb_ssid = QComboBox()
        self.cb_ssid.setEditable(True)
        self.cb_ssid.setView(QListView())
        self.cb_ssid.view().setMinimumWidth(self._s(300))
        ssid_row.addWidget(self.cb_ssid, 1)
        self.btn_scan = QPushButton(STRINGS[self.lang].get("search", "搜索"))
        self.btn_scan.setFixedSize(self._s(60), self._s(35))
        self.btn_scan.setStyleSheet("\n            QPushButton {\n                background-color: transparent;\n                border: 1px solid rgba(255, 255, 255, 0.2);\n                border-radius: 4px;\n                color: #B0BEC5;\n                font-family: 'Microsoft YaHei';\n                font-size: 9pt;\n                padding: 0px;\n            }\n            QPushButton:hover {\n                border: 1px solid #FA8F01;\n                color: #FFFFFF;\n            }\n        ")
        self.btn_scan.clicked.connect(self.scan_wifi)
        ssid_row.addWidget(self.btn_scan)
        layout_wifi.addLayout(ssid_row)
        self.lbl_pwd = QLabel(STRINGS[self.lang].get("password", "密码:"))
        self.lbl_pwd.setProperty("class", "aux-text")
        self.lbl_pwd.setStyleSheet("color: #78909C;")
        layout_wifi.addWidget(self.lbl_pwd)
        self.txt_pwd = QLineEdit()
        self.txt_pwd.setEchoMode(QLineEdit.Password)
        self.txt_pwd.setPlaceholderText("Password (if needed)")
        pwd_row = QHBoxLayout()
        pwd_row.addWidget(self.txt_pwd)
        self.chk_show_pwd = QCheckBox(STRINGS[self.lang].get("chk_show_pwd", "显示"))
        self.chk_show_pwd.setStyleSheet("color: #78909C;")
        self.chk_show_pwd.toggled.connect(lambda checked: self.txt_pwd.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password))
        pwd_row.addWidget(self.chk_show_pwd)
        layout_wifi.addLayout(pwd_row)
        last_ssid = self.settings.value("wifi/last_ssid", "")
        if last_ssid:
            self.cb_ssid.setCurrentText(last_ssid)
            saved_pwd = self.settings.value(f"wifi/pwd/{last_ssid}", "")
            if saved_pwd:
                self.txt_pwd.setText(saved_pwd)
        self.cb_ssid.currentTextChanged.connect(self._on_ssid_changed)
        layout_wifi.addStretch()
        self.stack_comm.addWidget(page_wifi)
        comm_layout.addWidget(self.stack_comm)
        self.cb_method.currentIndexChanged.connect(lambda i: self.stack_comm.setCurrentIndex(i))
        conn_widget = QWidget()
        conn_widget.setFixedHeight(self._s(28))
        conn_widget.setStyleSheet("QWidget { background: transparent; border: none; }")
        conn_row = QHBoxLayout(conn_widget)
        conn_row.setContentsMargins(15, 0, 0, 0)
        conn_row.setSpacing(4)
        self.lbl_off = QLabel(STRINGS[self.lang].get("lbl_toggle_off", "OFF"))
        self.lbl_off.setStyleSheet("color: #B0BEC5; font-size: 10pt;")
        self.lbl_off.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        conn_row.addWidget(self.lbl_off)
        self.btn_conn = QPushButton()
        self.btn_conn.setCheckable(True)
        self.btn_conn.setFixedSize(self._s(50), self._s(20))
        self.btn_conn.clicked.connect(self.toggle_connect)
        self._toggle_knob = QLabel(self.btn_conn)
        self._toggle_knob.setFixedSize(self._s(16), self._s(16))
        self._toggle_knob.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._update_toggle_style(False)
        conn_row.addWidget(self.btn_conn)
        self.lbl_on = QLabel(STRINGS[self.lang].get("lbl_toggle_on", "ON"))
        self.lbl_on.setStyleSheet("color: #B0BEC5; font-size: 10pt;")
        self.lbl_on.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        conn_row.addWidget(self.lbl_on)
        conn_row.addStretch()
        self.lbl_conn_status = QLabel(STRINGS[self.lang]["status_disconnected"])
        self.lbl_conn_status.setStyleSheet("color: #78909C; font-size: 10pt;")
        conn_row.addWidget(self.lbl_conn_status)
        comm_layout.addWidget(conn_widget)
        sidebar_layout.addWidget(comm_container)
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(20, 2, 20, 10)
        self.btn_lang = QPushButton("English" if self.lang == "zh" else "中文")
        self.btn_lang.setFixedHeight(self._s(35))
        self.btn_lang.setStyleSheet("\n            QPushButton {\n                background-color: #343645;\n                color: #FFFFFF;\n                border: 1px solid rgba(255,255,255,0.1);\n                border-radius: 4px;\n                font-size: 9pt;\n                padding: 0 10px;\n            }\n            QPushButton:hover {\n                border-color: #FA8F01;\n            }\n        ")
        self.btn_lang.clicked.connect(self.toggle_language)
        lang_row.addWidget(self.btn_lang)
        sidebar_layout.addLayout(lang_row)
        main_layout.addWidget(self.sidebar)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.header_lbl = QLabel(STRINGS[self.lang]["tab_servo"])
        self.header_lbl.setProperty("class", "title-text")
        self.header_lbl.setStyleSheet("QLabel { padding: 12px 15px; background-color: #1E1F31; font-weight: bold; font-size: 14pt; }")
        content_layout.addWidget(self.header_lbl)
        self.stack = QStackedWidget()
        self.tab_servo = ServoTab(self.comm_manager, self.lang)
        self.tab_coord = CoordTab(self.comm_manager, self.lang)
        self.tab_peripheral = PeripheralTab(self.comm_manager, self.lang)
        self.tab_system = SystemTab(self.comm_manager, self.lang)
        self.tab_ai = AITab(self.comm_manager, self.lang)
        self.tab_servo_adv = ServoAdvancedTab(self.comm_manager, self.lang)
        self.tab_teach = TeachTab(self.comm_manager, self.lang)
        self.stack.addWidget(self.tab_servo)
        self.stack.addWidget(self.tab_coord)
        self.stack.addWidget(self.tab_peripheral)
        self.stack.addWidget(self.tab_system)
        self.stack.addWidget(self.tab_ai)
        self.stack.addWidget(self.tab_servo_adv)
        self.stack.addWidget(self.tab_teach)
        content_layout.addWidget(self.stack, 1)
        self.log_widget = LogWidget(self.comm_manager, self.lang)
        self.log_widget.setMaximumHeight(self._s(150))
        self.content_layout = content_layout
        self.tab_servo.left_pane_layout.addWidget(self.log_widget)
        main_layout.addWidget(content_container, 1)

    def on_nav_changed(self, index):
        self.stack.setCurrentIndex(index)
        text = self.nav_list.item(index).text()
        self.header_lbl.setText(text)
        if index == 0:
            if hasattr(self, "tab_servo"):
                self.tab_servo.sync_current_servo_positions()
            elif index == 1 and hasattr(self, "tab_coord"):
                self.comm_manager.send_sys(CMD_GET_CUR_COORDS)
            if hasattr(self, "log_widget"):
                if index == 0:
                    if hasattr(self.tab_servo, "left_pane_layout"):
                        self.log_widget.setMinimumHeight(self._s(100))
                        self.log_widget.setMaximumHeight(self._s(150))
                        self.log_widget.show()
                        self.tab_servo.left_pane_layout.addWidget(self.log_widget)
        else:
            pass
        if hasattr(self, "content_layout"):
            self.log_widget.setMinimumHeight(self._s(100))
            self.log_widget.setMaximumHeight(self._s(150))
            self.log_widget.show()
            self.content_layout.addWidget(self.log_widget)

    def connect_signals(self):
        self.comm_manager.connection_status_changed.connect(self.update_connection_status)
        self.comm_manager.wifi_scan_finished.connect(self.on_wifi_scan_finished)

    def refresh_ports(self):
        self.cb_port.clear()
        ports = self.comm_manager.get_available_ports()
        self.cb_port.addItems(ports)

    def scan_wifi(self):
        self.btn_scan.setEnabled(False)
        self.comm_manager.scan_for_devices()

    def _on_ssid_changed(self, ssid):
        if ssid:
            saved_pwd = self.settings.value(f"wifi/pwd/{ssid}", "")
            self.txt_pwd.setText(saved_pwd)

    def on_wifi_scan_finished(self, networks):
        self.btn_scan.setEnabled(True)
        if networks:
            current = self.cb_ssid.currentText()
            self.cb_ssid.clear()
            self.cb_ssid.addItems(networks)
            if current and current not in networks:
                self.cb_ssid.addItem(current)
                self.cb_ssid.setCurrentText(current)
        elif networks:
            self.cb_ssid.setCurrentIndex(0)
        else:
            self.log_widget.append_text_log("No WiFi networks found. Please check: 1) WLAN AutoConfig service is running (services.msc) 2) Run as Administrator 3) WiFi adapter driver is installed")

    def toggle_connect(self):
        if self.comm_manager.is_connected:
            self.comm_manager.disconnect()
        else:
            method_idx = self.cb_method.currentIndex()
            if method_idx == 0:
                port = self.cb_port.currentText()
                if not port:
                    self.update_connection_status(False, "No port selected")
                    return
                try:
                    self.comm_manager.connect(port)
                except Exception as e:
                    try:
                        self.update_connection_status(False, str(e))
                    finally:
                        e = None
                        del e

            else:
                ssid = self.cb_ssid.currentText()
                if ssid:
                    pwd = self.txt_pwd.text()
                    self.settings.setValue("wifi/last_ssid", ssid)
                    if pwd:
                        self.settings.setValue(f"wifi/pwd/{ssid}", pwd)
                    self.comm_manager.connect_to_ap_and_socket(ssid, pwd)

    def _update_toggle_style(self, on):
        s = self._s
        knob_sz = s(16)
        btn_w = s(50)
        btn_h = s(20)
        knob_style = f"\n            QLabel {{\n                background-color: #FFFFFF;\n                border-radius: {knob_sz // 2}px;\n                min-width: {knob_sz}px; max-width: {knob_sz}px;\n                min-height: {knob_sz}px; max-height: {knob_sz}px;\n            }}\n        "
        btn_base = f"\n                    border: none;\n                    border-radius: {btn_h // 2}px;\n                    padding: 0px;\n                    margin: 0px;\n                    min-width: {btn_w}px; max-width: {btn_w}px;\n                    min-height: {btn_h}px; max-height: {btn_h}px;\n        "
        if on:
            self.btn_conn.setStyleSheet(f"\n                QPushButton {{\n                    background-color: #FA8F01;\n                    {btn_base}\n                }}\n                QPushButton:hover, QPushButton:pressed {{\n                    background-color: #FA8F01;\n                    {btn_base}\n                }}\n            ")
            self._toggle_knob.setStyleSheet(knob_style)
            self._toggle_knob.move(btn_w - knob_sz - s(2), s(2))
        else:
            self.btn_conn.setStyleSheet(f"\n                QPushButton {{\n                    background-color: #3A3C4E;\n                    {btn_base}\n                }}\n                QPushButton:hover, QPushButton:pressed {{\n                    background-color: #3A3C4E;\n                    {btn_base}\n                }}\n            ")
            self._toggle_knob.setStyleSheet(knob_style)
            self._toggle_knob.move(s(2), s(2))

    def update_connection_status(self, is_connected, message):
        self.btn_conn.setChecked(is_connected)
        self._update_toggle_style(is_connected)
        if is_connected:
            self.lbl_conn_status.setText(STRINGS[self.lang]["status_connected"])
            self.lbl_conn_status.setStyleSheet("color: #4CAF50; font-size: 10pt; font-weight: bold;")
            self.lbl_status.setText(STRINGS[self.lang]["status_connected"])
            self.status_dot.setStyleSheet("color: #4CAF50; font-size: 11pt; background: transparent;")
        else:
            self.lbl_conn_status.setText(STRINGS[self.lang]["status_disconnected"])
            self.lbl_conn_status.setStyleSheet("color: #78909C; font-size: 10pt;")
            self.lbl_status.setText(STRINGS[self.lang]["status_disconnected"])
            self.status_dot.setStyleSheet("color: #F44336; font-size: 11pt; background: transparent;")
        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)
        if message:
            if message != "Disconnected":
                if is_connected:
                    self.log_widget.append_text_log(f"Info: {message}")
                else:
                    self.log_widget.append_text_log(f"Connection Error: {message}")
