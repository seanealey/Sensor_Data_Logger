# ESP32 Logger GUI Template

A Python GUI for detecting ESP32 logger devices, selecting sensors, sending serial commands, and saving incoming samples to CSV.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Run

```bash
esp32-logger-gui
```

Or:

```bash
python -m esp32_logger_gui.main
```

## Expected ESP32 Serial Protocol

The GUI expects the ESP32 to identify itself with something like:

```text
DEVICE,bench_01
SENSORS,0:load_cell,1:encoder,2:temperature
```

Commands sent from GUI to ESP32:

```text
CONFIG,0,1,2
START
PAUSE
STOP
START_TIMED,10.0
```

Data from ESP32 should be CSV-like:

```text
DATA,12345,0,56.2
DATA,12345,1,1024
DATA,12345,2,24.8
```

Format:

```text
DATA,<time_ms>,<sensor_index>,<value>
```
