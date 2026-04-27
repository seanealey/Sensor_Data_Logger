from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SensorInfo:
    index: int
    name: str


@dataclass
class DataSample:
    time_ms: int
    sensor_index: int
    value: float


def parse_device_and_sensors(line: str) -> tuple[str, list[SensorInfo]] | None:
    parts = line.split(",")

    # Expect: NODE,<name>,SENSORS,<count>,<sensor names...>
    if len(parts) < 5:
        return None

    if parts[0] != "NODE" or parts[2] != "SENSORS":
        return None

    device_name = parts[1]

    try:
        sensor_count = int(parts[3])
    except ValueError:
        return None

    sensor_names = parts[4:]

    sensors: list[SensorInfo] = []

    for i, name in enumerate(sensor_names):
        sensors.append(SensorInfo(index=i, name=name.strip()))

    return device_name, sensors

def parse_data_sample(line: str) -> list[DataSample] | None:
    if not line.startswith("DATA"):
        return None

    parts = [p.strip() for p in line.split(",")]

    try:
        # Must have at least DATA + time + 1 sensor
        if len(parts) < 3:
            return None

        time_ms = int(float(parts[1])/ 1000) 

        samples = []
        for i, value_str in enumerate(parts[2:]):
            samples.append(
                DataSample(
                    time_ms=time_ms,
                    sensor_index=i,
                    value=float(value_str),
                )
            )

        return samples

    except ValueError:
        return None
def build_config_command(sensor_indices: list[int]) -> str:
    joined = ",".join(str(index) for index in sensor_indices)
    return f"SELECT,{joined}"
