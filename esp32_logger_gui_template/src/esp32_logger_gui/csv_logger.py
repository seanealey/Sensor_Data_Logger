from __future__ import annotations

import csv
from pathlib import Path

from esp32_logger_gui.protocol import DataSample, SensorInfo


class CsvLogger:
    def __init__(self) -> None:
        self._file = None
        self._writer: csv.writer | None = None
        self._sample_counter = 0
        self._selected_sensors: list[SensorInfo] = []
        self._sensor_lookup: dict[int, str] = {}

        self._current_time_ms: int | None = None
        self._current_row: dict[str, float | int | str] = {}

    @property
    def is_open(self) -> bool:
        return self._file is not None

    def open(self, path: str | Path, sensors: list[SensorInfo]) -> None:
        self.close()

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self._selected_sensors = sensors
        self._sensor_lookup = {sensor.index: sensor.name for sensor in sensors}

        self._file = path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)

        header = ["time_ms"] + [sensor.name for sensor in sensors]
        self._writer.writerow(header)

        self._current_time_ms = None
        self._current_row = {}
        self._sample_counter = 0

    def write_sample(self, sample: DataSample) -> None:
        if not self._writer:
            return

        sensor_name = self._sensor_lookup.get(sample.sensor_index)

        # Ignore data from sensors that were not selected
        if sensor_name is None:
            return

        if sample.time_ms == 0:
            self._sample_counter += 1
            sample.time_ms = self._sample_counter
        # First sample
        if self._current_time_ms is None:
            self._start_new_row(sample.time_ms)

        # New timestamp means previous row is complete enough to write
        if sample.time_ms != self._current_time_ms:
            self._write_current_row()
            self._start_new_row(sample.time_ms)

        self._current_row[sensor_name] = sample.value

    def close(self) -> None:
        if self._writer and self._current_row:
            self._write_current_row()

        if self._file:
            self._file.flush()
            self._file.close()

        self._file = None
        self._writer = None
        self._selected_sensors = []
        self._sensor_lookup = {}
        self._current_time_ms = None
        self._current_row = {}

    def _start_new_row(self, time_ms: int) -> None:
        self._current_time_ms = time_ms
        self._current_row = {"time_ms": time_ms}

    def _write_current_row(self) -> None:
        if not self._writer or self._current_time_ms is None:
            return

        row = [self._current_time_ms]

        for sensor in self._selected_sensors:
            row.append(self._current_row.get(sensor.name, ""))

        self._writer.writerow(row)