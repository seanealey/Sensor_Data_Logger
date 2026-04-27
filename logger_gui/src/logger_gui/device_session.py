from __future__ import annotations

from pathlib import Path

from logger_gui.csv_logger import CsvLogger
from logger_gui.protocol import SensorInfo
from logger_gui.serial_interface import SerialConnection


class DeviceSession:
    """Runtime state and control methods for one connected logger device."""

    def __init__(self, port: str, connection: SerialConnection) -> None:
        self.port = port
        self.connection = connection
        self.name = port
        self.sensors: list[SensorInfo] = []
        self.logger = CsvLogger()
        self.recording = False
        self.paused = False

    @property
    def is_connected(self) -> bool:
        return self.connection.is_connected

    def set_device_info(self, name: str, sensors: list[SensorInfo]) -> None:
        self.name = name
        self.sensors = sensors

    def send(self, command: str) -> None:
        if not self.connection or not self.connection.is_connected:
            raise RuntimeError(f"Device {self.name} is not connected")
        self.connection.write_line(command)

    def start(self, file_path: str | Path, selected_sensors: list[SensorInfo]) -> None:
        if not selected_sensors:
            raise ValueError("Select at least one sensor")

        self.logger.open(file_path, selected_sensors)
        selected_indices = [sensor.index for sensor in selected_sensors]

        command = "SELECT, " + ", ".join(str(i) for i in selected_indices)
        self.send(command)
        self.send("START")

        self.recording = True
        self.paused = False

    def pause(self) -> None:
        self.send("PAUSE")
        self.paused = True

    def stop(self) -> None:
        self.send("STOP")
        self.logger.close()
        self.recording = False
        self.paused = False

    def start_timed(
        self,
        path: str,
        selected_sensors: list[SensorInfo],
        duration_seconds: float,
    ) -> None:
        self.logger.open(path, selected_sensors)

        selected_indices = [sensor.index for sensor in selected_sensors]
        command = "Select, " + ", ".join(str(i) for i in selected_indices)

        self.send(command)
        self.send(f"START_TIMED,{duration_seconds}")

        self.recording = True

    def disconnect(self) -> None:
        if self.recording:
            try:
                self.stop()
            except Exception:
                self.logger.close()
                self.recording = False

        self.connection.disconnect()
