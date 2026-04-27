from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

import serial
from serial.tools import list_ports


@dataclass
class SerialDevice:
    port: str
    description: str
    hwid: str


def list_serial_devices() -> list[SerialDevice]:
    devices: list[SerialDevice] = []

    for port in list_ports.comports():
        devices.append(
            SerialDevice(
                port=port.device,
                description=port.description or "Unknown device",
                hwid=port.hwid or "",
            )
        )

    return devices


class SerialConnection:
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate
        self._serial: serial.Serial | None = None
        self._reader_thread: threading.Thread | None = None
        self._running = False
        self._write_lock = threading.Lock()

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def connect(self) -> None:
        self._serial = serial.Serial(self.port, self.baudrate, timeout=0.1)
        time.sleep(2.0)

        assert self._serial is not None
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()

    def disconnect(self) -> None:
        self.stop_reader()

        if self._serial and self._serial.is_open:
            self._serial.close()

        self._serial = None

    def write_line(self, line: str) -> None:
        if not self.is_connected:
            raise RuntimeError("Serial device is not connected")

        assert self._serial is not None

        with self._write_lock:
            self._serial.write((line.strip() + "\n").encode("utf-8"))
            self._serial.flush()

    def start_reader(self, callback: Callable[[str], None]) -> None:
        if not self.is_connected:
            raise RuntimeError("Serial device is not connected")

        if self._reader_thread and self._reader_thread.is_alive():
            return

        self._running = True
        self._reader_thread = threading.Thread(
            target=self._read_loop,
            args=(callback,),
            daemon=True,
        )
        self._reader_thread.start()

    def stop_reader(self) -> None:
        self._running = False

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1.0)

        self._reader_thread = None

    def _read_loop(self, callback: Callable[[str], None]) -> None:
        assert self._serial is not None

        while self._running:
            try:
                raw = self._serial.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="replace").strip()
                if line:
                    callback(line)

            except serial.SerialException:
                self._running = False
                callback("ERROR,Serial disconnected")

            except OSError:
                self._running = False
                callback("ERROR,Serial disconnected")