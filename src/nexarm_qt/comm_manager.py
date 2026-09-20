import os
import socket
import struct
import threading
import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal
from nexarm_qt.constants import *


class CommManager(QObject):
    connection_status_changed = pyqtSignal(bool, str)
    log_message_received = pyqtSignal(str)
    hex_log_received = pyqtSignal(str, bytes)
    packet_received = pyqtSignal(int, int, bytes)
    coord_updated = pyqtSignal(float, float, float, float, float, float, list)
    firmware_version_received = pyqtSignal(str, str)
    servo_offset_received = pyqtSignal(int, int)
    servo_pid_received = pyqtSignal(int, int, int, int)
    battery_level_received = pyqtSignal(float)
    wifi_scan_finished = pyqtSignal(list)
    servo_overload_received = pyqtSignal(int, int)
    servo_baud_received = pyqtSignal(int, int)
    servo_max_torque_received = pyqtSignal(int, int)
    servo_angle_limit_received = pyqtSignal(int, int, int)
    coord_limits_received = pyqtSignal(list)
    chassis_config_received = pyqtSignal(int, int)
    kinematics_config_received = pyqtSignal(list)
    channel_scan_received = pyqtSignal(list)
    sync_teach_status_received = pyqtSignal(int)
    action_edit_status_received = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.ser = None
        self.sock = None
        self.connection_type = "serial"
        self.is_connected = False
        self.stop_threads = False
        self.rx_buffer = bytearray()
        self.tx_lock = threading.Lock()
        self.last_p = [0.0, 0.0, 0.0]
        self.last_r = [0.0, 0.0]
        self.last_claw = 0.0
        self.last_servos = [0] * 6
        self.servo_offsets = {i: 0 for i in range(1, 7)}

    def get_available_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, port_name):
        if self.is_connected:
            return
        try:
            self.connection_type = "serial"
            self.ser = serial.Serial(port_name, 1000000, timeout=0.01)
            self.is_connected = True
            self.stop_threads = False
            threading.Thread(target=self.rx_loop, daemon=True).start()
            self._read_all_offsets()
            self.connection_status_changed.emit(True, f"Connected to {port_name}")
        except (serial.SerialException, PermissionError) as e:
            self.connection_status_changed.emit(False, f"Port {port_name} is busy or no permission")
        except Exception as e:
            self.connection_status_changed.emit(False, f"Serial Error: {e}")

    def connect_wifi(self, ip, port=8080, silent=False):
        if self.is_connected:
            return
        try:
            self.connection_type = "wifi"
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((ip, int(port)))
            self.sock.settimeout(0.01)
            self.is_connected = True
            self.stop_threads = False
            threading.Thread(target=self.rx_loop, daemon=True).start()
            self._read_all_offsets()
            if not silent:
                self.connection_status_changed.emit(True, f"Connected to {ip}:{port}")
        except Exception as e:
            if not silent:
                self.connection_status_changed.emit(False, f"WiFi Connection Error: {e}")

    def disconnect(self):
        if not self.is_connected:
            return
        self.is_connected = False
        self.stop_threads = True
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        self.connection_status_changed.emit(False, "Disconnected")

    def rx_loop(self):
        while self.is_connected and not self.stop_threads:
            try:
                if self.connection_type == "serial" and self.ser:
                    n = self.ser.in_waiting
                    if n > 0:
                        data = self.ser.read(n)
                        if data:
                            self.rx_buffer.extend(data)
                            self.process_buffer()
                elif self.connection_type == "wifi" and self.sock:
                    try:
                        data = self.sock.recv(1024)
                        if data:
                            self.rx_buffer.extend(data)
                            self.process_buffer()
                    except socket.timeout:
                        pass
                    except Exception:
                        self.disconnect()
                        break
            except (serial.SerialException, OSError):
                print("Serial port disconnected (cable removed)")
                self.disconnect()
                break
            except Exception as e:
                print(f"RX Error: {e}")
            time.sleep(0.005)

    def process_buffer(self):
        while len(self.rx_buffer) >= 7:
            if self.rx_buffer[0] != 255 or self.rx_buffer[1] != 255:
                self.rx_buffer.pop(0)
                continue
            length = self.rx_buffer[3]
            total_len = length + 4
            if len(self.rx_buffer) < total_len:
                return
            packet = self.rx_buffer[:total_len]
            self.rx_buffer = self.rx_buffer[total_len:]
            self.hex_log_received.emit("RX", bytes(packet))
            id_val = packet[2]
            cmd = packet[4]
            data = bytes(packet[5:-1])
            self.handle_packet(id_val, cmd, data)

    def _decode_servo_offset(self, data):
        if len(data) >= 3:
            s_id = data[0]
            offset = struct.unpack("<h", data[1:3])[0]
            self.servo_offsets[s_id] = offset
            return (s_id, offset)
        return (0, 0)

    def handle_packet(self, id_val, cmd, data):
        self.packet_received.emit(id_val, cmd, data)

        if cmd in (CMD_GET_CUR_COORDS, CMD_FKINE_RESULT_GET) and len(data) >= 12:
            try:
                coords = struct.unpack("<hhh", data[:6])
                self.last_p = [c / 10.0 for c in coords]
                if len(data) >= 18:
                    angles = struct.unpack("<hhh", data[6:12])
                    self.last_r = [a / 10.0 for a in angles[:2]]
                if len(data) >= 24:
                    servos = list(struct.unpack("<hhhhhh", data[12:24]))
                    self.last_servos = servos
                self.coord_updated.emit(
                    self.last_p[0], self.last_p[1], self.last_p[2],
                    self.last_r[0], self.last_r[1], self.last_claw,
                    self.last_servos
                )
            except Exception as e:
                print(f"Coord Parse Error: {e}")

        elif cmd == CMD_FIRMWARE_VERSION_CHECK:
            v_esp = data.decode("utf-8", errors="ignore") if data else "Unknown"
            self.firmware_version_received.emit(v_esp, "")

        elif cmd == CMD_CHECK_BAT_LEVEL_CHECK and len(data) >= 2:
            bat = struct.unpack("<H", data[:2])[0] / 100.0
            self.battery_level_received.emit(bat)

        elif cmd == CMD_GET_POS_OFFSET:
            s_id, off = self._decode_servo_offset(data)
            self.servo_offset_received.emit(s_id, off)

        elif cmd == CMD_GET_PID_PARAM and len(data) >= 5:
            s_id, p, i, d = struct.unpack("<BBBB", data[:4])
            self.servo_pid_received.emit(s_id, p, i, d)

        elif cmd == CMD_READ_OVERLOAD and len(data) >= 2:
            s_id, ov = struct.unpack("<BB", data[:2])
            self.servo_overload_received.emit(s_id, ov)

        elif cmd == CMD_READ_BAUD and len(data) >= 2:
            s_id, bd = struct.unpack("<BB", data[:2])
            self.servo_baud_received.emit(s_id, bd)

        elif cmd == CMD_READ_MAX_TORQUE and len(data) >= 3:
            s_id = data[0]
            tq = struct.unpack("<H", data[1:3])[0]
            self.servo_max_torque_received.emit(s_id, tq)

        elif cmd == CMD_READ_ANGLE_LIMIT and len(data) >= 5:
            s_id = data[0]
            min_a, max_a = struct.unpack("<HH", data[1:5])
            self.servo_angle_limit_received.emit(s_id, min_a, max_a)

        elif cmd == CMD_GET_COORD_LIMITS and len(data) >= 24:
            limits = list(struct.unpack("<hhhhhhhhhhhh", data[:24]))
            self.coord_limits_received.emit(limits)

        elif cmd == CMD_GET_CHASSIS_CONFIG and len(data) >= 2:
            c_type, c_mode = struct.unpack("<BB", data[:2])
            self.chassis_config_received.emit(c_type, c_mode)

        elif cmd == CMD_GET_KINEMATICS_PARAM:
            self.kinematics_config_received.emit(list(data))

    def send_packet(self, id_val, cmd, args=None):
        if not self.is_connected:
            return
        if args is None:
            args = []
        try:
            length = len(args) + 2
            payload = [id_val, length, cmd] + list(args)
            checksum = (~sum(payload)) & 0xFF
            packet = bytes([0xFF, 0xFF] + payload + [checksum])
            with self.tx_lock:
                if self.connection_type == "serial" and self.ser:
                    self.ser.write(packet)
                elif self.connection_type == "wifi" and self.sock:
                    self.sock.sendall(packet)
                self.hex_log_received.emit("TX", packet)
        except Exception as e:
            print(f"TX Error: {e}")

    def send_sys(self, cmd, args=None):
        if args is None:
            args = []
        self.send_packet(255, cmd, args)

    def _read_all_offsets(self):
        for i in range(1, 7):
            self.send_packet(i, CMD_GET_POS_OFFSET)
            time.sleep(0.01)

    def scan_for_devices(self):
        pass

    def connect_to_ap_and_socket(self, ssid, password):
        pass
