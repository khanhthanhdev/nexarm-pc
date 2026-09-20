# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.14.6 | packaged by Anaconda, Inc. | (main, Jun 18 2026, 21:18:42) [MSC v.1942 64 bit (AMD64)]
# Embedded file name: nexarm_qt\ui\teach_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel, QGridLayout, QScrollArea
from PyQt5.QtCore import Qt
from nexarm_qt.constants import *
from nexarm_qt.translations import STRINGS
from nexarm_qt.styles import S

class TeachTab(QWidget):

    def __init__(self, comm_manager, lang='zh'):
        super().__init__()
        self.comm_manager = comm_manager
        self.lang = lang
        self._action_editing = False
        self._action_recording = False
        self._action_playing = False
        self._sync_editing = False
        self._sync_recording = False
        self._sync_playing = False
        self.setup_ui()
        self.comm_manager.sync_teach_status_received.connect(self._on_sync_status)
        self.comm_manager.action_edit_status_received.connect(self._on_action_status)

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        self.grp_action = QGroupBox(STRINGS[self.lang].get("grp_action_edit", "动作编辑"))
        self._build_action_edit(self.grp_action)
        layout.addWidget(self.grp_action)
        self.grp_sync = QGroupBox(STRINGS[self.lang].get("grp_sync_teach", "同步器示教"))
        self._build_sync_teach(self.grp_sync)
        layout.addWidget(self.grp_sync)
        layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _build_action_edit(self, grp):
        grid = QGridLayout(grp)
        grid.setSpacing(10)
        s = STRINGS[self.lang]
        self.btn_ae_enter = QPushButton(s.get("btn_teach_enter", "进入编辑"))
        self.btn_ae_exit = QPushButton(s.get("btn_teach_exit", "退出编辑"))
        self.btn_ae_rec = QPushButton(s.get("btn_teach_rec_start", "开始录制"))
        self.btn_ae_rec_stop = QPushButton(s.get("btn_teach_rec_stop", "停止录制"))
        self.btn_ae_play = QPushButton(s.get("btn_teach_play", "播放动作"))
        self.btn_ae_play_stop = QPushButton(s.get("btn_teach_play_stop", "停止播放"))
        self.btn_ae_clear = QPushButton(s.get("btn_teach_clear", "清除动作"))
        self.btn_ae_query = QPushButton(s.get("btn_teach_query", "查询状态"))
        self.lbl_ae_status = QLabel(s.get("lbl_teach_idle", "空闲"))
        self.lbl_ae_status.setStyleSheet("color: #FA8F01; font-size: 11pt; font-weight: bold;")
        self.lbl_ae_status.setAlignment(Qt.AlignCenter)
        self.lbl_ae_frames = QLabel(s.get("lbl_frames", "帧数") + ": --")
        self.lbl_ae_frames.setStyleSheet("color: #B0BEC5; font-size: 10pt;")
        self.lbl_ae_frames.setAlignment(Qt.AlignCenter)
        self._style_btn(self.btn_ae_enter, "blue")
        self._style_btn(self.btn_ae_exit, "gray")
        self._style_btn(self.btn_ae_rec, "orange")
        self._style_btn(self.btn_ae_rec_stop, "red")
        self._style_btn(self.btn_ae_play, "green")
        self._style_btn(self.btn_ae_play_stop, "red")
        self._style_btn(self.btn_ae_clear, "red")
        self._style_btn(self.btn_ae_query, "gray")
        grid.addWidget(self.lbl_ae_status, 0, 0, 1, 2)
        grid.addWidget(self.lbl_ae_frames, 1, 0, 1, 2)
        grid.addWidget(self.btn_ae_enter, 2, 0)
        grid.addWidget(self.btn_ae_exit, 2, 1)
        grid.addWidget(self.btn_ae_rec, 3, 0)
        grid.addWidget(self.btn_ae_rec_stop, 3, 1)
        grid.addWidget(self.btn_ae_play, 4, 0)
        grid.addWidget(self.btn_ae_play_stop, 4, 1)
        grid.addWidget(self.btn_ae_clear, 5, 0)
        grid.addWidget(self.btn_ae_query, 5, 1)
        self.btn_ae_exit.setEnabled(False)
        self.btn_ae_rec.setEnabled(False)
        self.btn_ae_rec_stop.setEnabled(False)
        self.btn_ae_play.setEnabled(False)
        self.btn_ae_play_stop.setEnabled(False)
        self.btn_ae_clear.setEnabled(False)
        self.btn_ae_enter.clicked.connect(self._ae_enter)
        self.btn_ae_exit.clicked.connect(self._ae_exit)
        self.btn_ae_rec.clicked.connect(self._ae_rec_start)
        self.btn_ae_rec_stop.clicked.connect(self._ae_rec_stop)
        self.btn_ae_play.clicked.connect(self._ae_play)
        self.btn_ae_play_stop.clicked.connect(self._ae_play_stop)
        self.btn_ae_clear.clicked.connect(self._ae_clear)
        self.btn_ae_query.clicked.connect(self._ae_query)

    def _ae_enter(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_ENTER)
        self._action_editing = True
        self._update_ae_btns()
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_editing", "编辑模式"))

    def _ae_exit(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_EXIT)
        self._action_editing = False
        self._action_recording = False
        self._action_playing = False
        self._update_ae_btns()
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_idle", "空闲"))

    def _ae_rec_start(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_START)
        self._action_recording = True
        self._update_ae_btns()
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_recording", "录制中..."))

    def _ae_rec_stop(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_STOP)
        self._action_recording = False
        self._update_ae_btns()
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_editing", "编辑模式"))

    def _ae_play(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_PLAY)
        self._action_playing = True
        self._update_ae_btns()
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_playing", "播放中..."))

    def _ae_play_stop(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_PLAY_STOP)
        self._action_playing = False
        self._update_ae_btns()
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_editing", "编辑模式"))

    def _ae_clear(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_CLEAR)
        self.lbl_ae_status.setText(STRINGS[self.lang].get("lbl_teach_editing", "编辑模式"))

    def _ae_query(self):
        self.comm_manager.send_sys(CMD_ACTION_EDIT_QUERY)

    def _update_ae_btns(self):
        e = self._action_editing
        r = self._action_recording
        p = self._action_playing
        self.btn_ae_enter.setEnabled(not e)
        self.btn_ae_exit.setEnabled(e and not r)
        self.btn_ae_rec.setEnabled(e and not r and not p)
        self.btn_ae_rec_stop.setEnabled(r)
        self.btn_ae_play.setEnabled(e and not r and not p)
        self.btn_ae_play_stop.setEnabled(p)
        self.btn_ae_clear.setEnabled(e and not r and not p)

    def _build_sync_teach(self, grp):
        grid = QGridLayout(grp)
        grid.setSpacing(10)
        s = STRINGS[self.lang]
        self.btn_st_enter = QPushButton(s.get("btn_sync_enter", "进入同步器示教"))
        self.btn_st_exit = QPushButton(s.get("btn_sync_exit", "退出同步器示教"))
        self.btn_st_rec = QPushButton(s.get("btn_teach_rec_start", "开始录制"))
        self.btn_st_rec_stop = QPushButton(s.get("btn_teach_rec_stop", "停止录制"))
        self.btn_st_play = QPushButton(s.get("btn_teach_play", "播放动作"))
        self.btn_st_play_stop = QPushButton(s.get("btn_teach_play_stop", "停止播放"))
        self.btn_st_clear = QPushButton(s.get("btn_sync_clear", "清空数据"))
        self.btn_st_query = QPushButton(s.get("btn_teach_query", "查询状态"))
        self.lbl_st_status = QLabel(s.get("lbl_teach_idle", "空闲"))
        self.lbl_st_status.setStyleSheet("color: #FA8F01; font-size: 11pt; font-weight: bold;")
        self.lbl_st_status.setAlignment(Qt.AlignCenter)
        self.lbl_st_frames = QLabel(s.get("lbl_frames", "帧数") + ": --")
        self.lbl_st_frames.setStyleSheet("color: #B0BEC5; font-size: 10pt;")
        self.lbl_st_frames.setAlignment(Qt.AlignCenter)
        self._style_btn(self.btn_st_enter, "blue")
        self._style_btn(self.btn_st_exit, "gray")
        self._style_btn(self.btn_st_rec, "orange")
        self._style_btn(self.btn_st_rec_stop, "red")
        self._style_btn(self.btn_st_play, "green")
        self._style_btn(self.btn_st_play_stop, "red")
        self._style_btn(self.btn_st_clear, "red")
        self._style_btn(self.btn_st_query, "gray")
        grid.addWidget(self.lbl_st_status, 0, 0, 1, 2)
        grid.addWidget(self.lbl_st_frames, 1, 0, 1, 2)
        grid.addWidget(self.btn_st_enter, 2, 0)
        grid.addWidget(self.btn_st_exit, 2, 1)
        grid.addWidget(self.btn_st_rec, 3, 0)
        grid.addWidget(self.btn_st_rec_stop, 3, 1)
        grid.addWidget(self.btn_st_play, 4, 0)
        grid.addWidget(self.btn_st_play_stop, 4, 1)
        grid.addWidget(self.btn_st_clear, 5, 0)
        grid.addWidget(self.btn_st_query, 5, 1)
        self.btn_st_exit.setEnabled(False)
        self.btn_st_rec.setEnabled(False)
        self.btn_st_rec_stop.setEnabled(False)
        self.btn_st_play.setEnabled(False)
        self.btn_st_play_stop.setEnabled(False)
        self.btn_st_clear.setEnabled(False)
        self.btn_st_enter.clicked.connect(self._st_enter)
        self.btn_st_exit.clicked.connect(self._st_exit)
        self.btn_st_rec.clicked.connect(self._st_rec_start)
        self.btn_st_rec_stop.clicked.connect(self._st_rec_stop)
        self.btn_st_play.clicked.connect(self._st_play)
        self.btn_st_play_stop.clicked.connect(self._st_play_stop)
        self.btn_st_clear.clicked.connect(self._st_clear)
        self.btn_st_query.clicked.connect(self._st_query)

    def _st_enter(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_ENTER)
        self._sync_editing = True
        self._update_st_btns()
        self.lbl_st_status.setText(STRINGS[self.lang].get("lbl_sync_editing", "同步器示教模式"))

    def _st_exit(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_EXIT)
        self._sync_editing = False
        self._sync_recording = False
        self._sync_playing = False
        self._update_st_btns()
        self.lbl_st_status.setText(STRINGS[self.lang].get("lbl_teach_idle", "空闲"))

    def _st_rec_start(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_REC_START)
        self._sync_recording = True
        self._update_st_btns()
        self.lbl_st_status.setText(STRINGS[self.lang].get("lbl_teach_recording", "录制中..."))

    def _st_rec_stop(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_REC_STOP)
        self._sync_recording = False
        self._update_st_btns()
        self.lbl_st_status.setText(STRINGS[self.lang].get("lbl_sync_editing", "同步器示教模式"))

    def _st_play(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_PLAY)
        self._sync_playing = True
        self._update_st_btns()
        self.lbl_st_status.setText(STRINGS[self.lang].get("lbl_teach_playing", "播放中..."))

    def _st_play_stop(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_PLAY_STOP)
        self._sync_playing = False
        self._update_st_btns()
        self.lbl_st_status.setText(STRINGS[self.lang].get("lbl_sync_editing", "同步器示教模式"))

    def _st_clear(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_CLEAR)
        self.lbl_st_frames.setText(STRINGS[self.lang].get("lbl_frames", "帧数") + ": 0")

    def _st_query(self):
        self.comm_manager.send_sys(CMD_SYNC_TEACH_QUERY)

    def _on_sync_status(self, mode, rec, play, count, overflow):
        s = STRINGS[self.lang]
        self._sync_editing = bool(mode)
        self._sync_recording = bool(rec)
        self._sync_playing = bool(play)
        self._update_st_btns()
        if overflow:
            self.lbl_st_status.setText(s.get("lbl_sync_overflow", "溢出!"))
            self.lbl_st_status.setStyleSheet("color: #F44336; font-size: 11pt; font-weight: bold;")
        else:
            if play:
                self.lbl_st_status.setText(s.get("lbl_teach_playing", "播放中..."))
                self.lbl_st_status.setStyleSheet("color: #FA8F01; font-size: 11pt; font-weight: bold;")
            else:
                if rec:
                    self.lbl_st_status.setText(s.get("lbl_teach_recording", "录制中..."))
                    self.lbl_st_status.setStyleSheet("color: #FA8F01; font-size: 11pt; font-weight: bold;")
                else:
                    if mode:
                        self.lbl_st_status.setText(s.get("lbl_sync_editing", "同步器示教模式"))
                        self.lbl_st_status.setStyleSheet("color: #FA8F01; font-size: 11pt; font-weight: bold;")
                    else:
                        self.lbl_st_status.setText(s.get("lbl_teach_idle", "空闲"))
                        self.lbl_st_status.setStyleSheet("color: #FA8F01; font-size: 11pt; font-weight: bold;")
        self.lbl_st_frames.setText(s.get("lbl_frames", "帧数") + f": {count}")

    def _on_action_status(self, mode, rec, play, count):
        s = STRINGS[self.lang]
        self._action_editing = bool(mode)
        self._action_recording = bool(rec)
        self._action_playing = bool(play)
        self._update_ae_btns()
        if play:
            self.lbl_ae_status.setText(s.get("lbl_teach_playing", "播放中..."))
        else:
            if rec:
                self.lbl_ae_status.setText(s.get("lbl_teach_recording", "录制中..."))
            else:
                if mode:
                    self.lbl_ae_status.setText(s.get("lbl_teach_editing", "编辑模式"))
                else:
                    self.lbl_ae_status.setText(s.get("lbl_teach_idle", "空闲"))
        self.lbl_ae_frames.setText(s.get("lbl_frames", "帧数") + f": {count}")

    def _update_st_btns(self):
        e = self._sync_editing
        r = self._sync_recording
        p = self._sync_playing
        self.btn_st_enter.setEnabled(not e)
        self.btn_st_exit.setEnabled(e and not r)
        self.btn_st_rec.setEnabled(e and not r and not p)
        self.btn_st_rec_stop.setEnabled(r)
        self.btn_st_play.setEnabled(e and not r and not p)
        self.btn_st_play_stop.setEnabled(p)
        self.btn_st_clear.setEnabled(e and not r and not p)

    def _style_btn(self, btn, color):
        colors = {
         'blue': ('#1976D2', '#1E88E5', '#1565C0'), 
         'orange': ('#FA8F01', '#FB8C00', '#E65100'), 
         'red': ('#D32F2F', '#E53935', '#B71C1C'), 
         'green': ('#388E3C', '#43A047', '#2E7D32'), 
         'gray': ('#546E7A', '#607D8B', '#37474F')}
        bg, hover, pressed = colors.get(color, colors["gray"])
        btn.setStyleSheet(f"\n            QPushButton {{\n                background-color: {bg}; color: white; font-weight: bold;\n                font-size: 10pt; padding: 10px 16px; border-radius: 5px;\n            }}\n            QPushButton:hover {{ background-color: {hover}; }}\n            QPushButton:pressed {{ background-color: {pressed}; }}\n            QPushButton:disabled {{ background-color: #455A64; color: #78909C; }}\n        ")

    def update_language(self, lang):
        self.lang = lang
        s = STRINGS[lang]
        self.grp_action.setTitle(s.get("grp_action_edit", "Action Edit"))
        self.grp_sync.setTitle(s.get("grp_sync_teach", "Sync Teach"))
        self.btn_ae_enter.setText(s.get("btn_teach_enter", "Enter Edit"))
        self.btn_ae_exit.setText(s.get("btn_teach_exit", "Exit Edit"))
        self.btn_ae_rec.setText(s.get("btn_teach_rec_start", "Start Record"))
        self.btn_ae_rec_stop.setText(s.get("btn_teach_rec_stop", "Stop Record"))
        self.btn_ae_play.setText(s.get("btn_teach_play", "Play"))
        self.btn_ae_play_stop.setText(s.get("btn_teach_play_stop", "Stop Play"))
        self.btn_ae_clear.setText(s.get("btn_teach_clear", "Clear"))
        self.btn_ae_query.setText(s.get("btn_teach_query", "Query"))
        self.btn_st_enter.setText(s.get("btn_sync_enter", "Enter Sync Teach"))
        self.btn_st_exit.setText(s.get("btn_sync_exit", "Exit Sync Teach"))
        self.btn_st_rec.setText(s.get("btn_teach_rec_start", "Start Record"))
        self.btn_st_rec_stop.setText(s.get("btn_teach_rec_stop", "Stop Record"))
        self.btn_st_play.setText(s.get("btn_teach_play", "Play"))
        self.btn_st_play_stop.setText(s.get("btn_teach_play_stop", "Stop Play"))
        self.btn_st_clear.setText(s.get("btn_sync_clear", "Clear Data"))
        self.btn_st_query.setText(s.get("btn_teach_query", "Query"))
        self.lbl_st_frames.setText(s.get("lbl_frames", "Frames") + ": --")
        self.lbl_ae_frames.setText(s.get("lbl_frames", "Frames") + ": --")
        if self._action_recording:
            self.lbl_ae_status.setText(s.get("lbl_teach_recording", "Recording..."))
        else:
            if self._action_playing:
                self.lbl_ae_status.setText(s.get("lbl_teach_playing", "Playing..."))
            else:
                if self._action_editing:
                    self.lbl_ae_status.setText(s.get("lbl_teach_editing", "Edit Mode"))
                else:
                    self.lbl_ae_status.setText(s.get("lbl_teach_idle", "Idle"))
        if self._sync_recording:
            self.lbl_st_status.setText(s.get("lbl_teach_recording", "Recording..."))
        else:
            if self._sync_playing:
                self.lbl_st_status.setText(s.get("lbl_teach_playing", "Playing..."))
            else:
                if self._sync_editing:
                    self.lbl_st_status.setText(s.get("lbl_sync_editing", "Sync Teach Mode"))
                else:
                    self.lbl_st_status.setText(s.get("lbl_teach_idle", "Idle"))
