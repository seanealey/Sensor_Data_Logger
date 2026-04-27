from __future__ import annotations

import queue
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from logger_gui.csv_logger import CsvLogger
from logger_gui.protocol import (
    SensorInfo,
    build_config_command,
    parse_data_sample
)
from logger_gui.protocol import parse_device_and_sensors
from logger_gui.serial_interface import SerialConnection, list_serial_devices


class LoggerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Logger GUI")
        self.geometry("850x560")

        self.connection: SerialConnection | None = None
        self.csv_logger = CsvLogger()
        self.incoming_lines: queue.Queue[str] = queue.Queue()

        self.sensors: list[SensorInfo] = []
        self.sensor_vars: dict[int, tk.BooleanVar] = {}

        self._build_ui()
        self.refresh_ports()
        self.after(50, self._process_incoming_lines)

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        top = ttk.LabelFrame(main, text="Device", padding=10)
        top.pack(fill=tk.X)

        self.port_combo = ttk.Combobox(top, state="readonly", width=45)
        self.port_combo.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(top, text="Refresh", command=self.refresh_ports).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Connect", command=self.connect_selected_port).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Disconnect", command=self.disconnect).pack(side=tk.LEFT, padx=4)

        self.device_label = ttk.Label(top, text="No device connected")
        self.device_label.pack(side=tk.LEFT, padx=16)

        middle = ttk.Frame(main)
        middle.pack(fill=tk.BOTH, expand=True, pady=10)

        sensor_box = ttk.LabelFrame(middle, text="Sensors", padding=10)
        sensor_box.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.sensor_frame = ttk.Frame(sensor_box)
        self.sensor_frame.pack(fill=tk.BOTH, expand=True)

        file_box = ttk.LabelFrame(middle, text="Output", padding=10)
        file_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_path_var = tk.StringVar(value=str(Path.cwd() / "test_log.csv"))

        ttk.Label(file_box, text="CSV file:").pack(anchor=tk.W)
        file_row = ttk.Frame(file_box)
        file_row.pack(fill=tk.X, pady=(4, 10))

        ttk.Entry(file_row, textvariable=self.output_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_row, text="Browse", command=self.browse_output_file).pack(side=tk.LEFT, padx=6)

        control_box = ttk.LabelFrame(main, text="Controls", padding=10)
        control_box.pack(fill=tk.X)

        ttk.Button(control_box, text="Start Recording", command=self.start_recording).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(control_box, text="Pause Recording", command=self.pause_recording).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(control_box, text="Stop Recording", command=self.stop_recording).pack(
            side=tk.LEFT, padx=4
        )

        ttk.Label(control_box, text="Timed length (s):").pack(side=tk.LEFT, padx=(20, 4))
        self.duration_var = tk.StringVar(value="10")
        ttk.Entry(control_box, textvariable=self.duration_var, width=8).pack(side=tk.LEFT)
        ttk.Button(control_box, text="Start Timed", command=self.start_timed_recording).pack(
            side=tk.LEFT, padx=4
        )

        log_box = ttk.LabelFrame(main, text="Serial Log", padding=10)
        log_box.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.log_text = tk.Text(log_box, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def refresh_ports(self) -> None:
        devices = list_serial_devices()
        values = [f"{device.port} | {device.description}" for device in devices]

        self.port_combo["values"] = values
        self._ports = devices

        if values:
            self.port_combo.current(0)

    def connect_selected_port(self) -> None:
        selected_index = self.port_combo.current()
        if selected_index < 0:
            messagebox.showwarning("No port selected", "Select a serial port first.")
            return

        device = self._ports[selected_index]

        try:
            self.connection = SerialConnection(device.port)
            self.connection.connect()
            self.connection.start_reader(self.incoming_lines.put)
            self.connection.write_line("HELLO")
            self._log("> HELLO")
            self.device_label.config(text=f"Connected: {device.port}")
            self._log(f"Connected to {device.port}")

        except Exception as exc:
            messagebox.showerror("Connection failed", str(exc))
            self.connection = None

    def disconnect(self) -> None:
        if self.connection:
            self.connection.disconnect()
            self.connection = None

        self.csv_logger.close()
        self.device_label.config(text="No device connected")
        self._log("Disconnected")

    def browse_output_file(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if path:
            self.output_path_var.set(path)

    def start_recording(self) -> None:
        selected = self._selected_sensor_indices()
        if not selected:
            messagebox.showwarning("No sensors selected", "Select at least one sensor.")
            return

        self._open_csv()
        self._send(build_config_command(selected))
        self._send("START")
        self._log("Recording started")

    def pause_recording(self) -> None:
        self._send("PAUSE")
        self._log("Recording paused")

    def stop_recording(self) -> None:
        self._send("STOP")
        self.csv_logger.close()
        self._log("Recording stopped and CSV closed")

    def start_timed_recording(self) -> None:
        selected = self._selected_sensor_indices()
        if not selected:
            messagebox.showwarning("No sensors selected", "Select at least one sensor.")
            return

        try:
            duration = float(self.duration_var.get())
        except ValueError:
            messagebox.showwarning("Invalid duration", "Enter a duration in seconds.")
            return

        self._open_csv()
        self._send(build_config_command(selected))
        self._send(f"START_TIMED,{duration}")
        self._log(f"Timed recording started for {duration} s")

    def _open_csv(self) -> None:
        selected_indices = set(self._selected_sensor_indices())
        selected_sensors = [sensor for sensor in self.sensors if sensor.index in selected_indices]
        self.csv_logger.open(self.output_path_var.get(), selected_sensors)

    def _send(self, command: str) -> None:
        if not self.connection or not self.connection.is_connected:
            raise RuntimeError("No serial device connected")

        self.connection.write_line(command)
        self._log(f"> {command}")

    def _selected_sensor_indices(self) -> list[int]:
        return [index for index, var in self.sensor_vars.items() if var.get()]

    def _process_incoming_lines(self) -> None:
        while not self.incoming_lines.empty():
            line = self.incoming_lines.get()
            self._handle_line(line)

        self.after(50, self._process_incoming_lines)

    def _handle_line(self, line: str) -> None:
        self._log(line)

        result = parse_device_and_sensors(line)
        if result:
            device_name, sensors = result
            self.device_label.config(text=f"Connected: {device_name}")
            self.sensors = sensors
            self._render_sensors()
            return

        sample = parse_data_sample(line)
        if sample is not None and self.csv_logger.is_open:
            self.csv_logger.write_sample(sample)

    def _render_sensors(self) -> None:
        for child in self.sensor_frame.winfo_children():
            child.destroy()

        self.sensor_vars.clear()

        for sensor in self.sensors:
            var = tk.BooleanVar(value=True)
            self.sensor_vars[sensor.index] = var

            ttk.Checkbutton(
                self.sensor_frame,
                text=f"{sensor.index}: {sensor.name}",
                variable=var,
            ).pack(anchor=tk.W)

    def _log(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
