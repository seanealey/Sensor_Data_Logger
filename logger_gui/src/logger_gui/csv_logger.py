from __future__ import annotations

import csv
from pathlib import Path

from logger_gui.protocol import DataSample, SensorInfo


class CsvLogger:
    def __init__(self) -> None:
        self._file = None
        self._writer: csv.writer | None = None
        self._sample_counter = 0

        self._selected_sensors: list[SensorInfo] = []
        self._sensor_lookup: dict[int, str] = {}

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

        self._sample_counter = 0

    def write_sample(self, samples: list[DataSample]) -> None:
        if not self._writer or not samples:
            return

        time_ms = samples[0].time_ms

        if time_ms == 0:
            self._sample_counter += 1
            time_ms = self._sample_counter

        row_data: dict[str, float] = {}

        for sample in samples:
            sensor_name = self._sensor_lookup.get(sample.sensor_index)

            # Ignore data from sensors that were not selected
            if sensor_name is None:
                continue

            row_data[sensor_name] = sample.value

        row = [time_ms]

        for sensor in self._selected_sensors:
            row.append(row_data.get(sensor.name, ""))

        self._writer.writerow(row)

    def close(self) -> None:
        if self._file:
            self._file.flush()
            self._file.close()

        self._file = None
        self._writer = None
        self._selected_sensors = []
        self._sensor_lookup = {}