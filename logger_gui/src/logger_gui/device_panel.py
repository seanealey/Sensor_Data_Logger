from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from logger_gui.device_session import DeviceSession
from logger_gui.protocol import SensorInfo


class DevicePanel(ttk.LabelFrame):
    """Tkinter panel that controls one DeviceSession independently."""

    def __init__(self, parent: tk.Widget, session: DeviceSession, log_callback) -> None:
        super().__init__(parent, text=f"{session.name} ({session.port})", padding=10)

        self.session = session
        self.log_callback = log_callback
        self.sensor_vars: dict[int, tk.BooleanVar] = {}
        self.output_path_var = tk.StringVar(value=self._default_output_path())
        self.duration_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()
        self.refresh_device_info()

    def _default_output_path(self) -> str:
        safe_name = self.session.name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        return str(Path.cwd() / f"test_log_{safe_name}.csv")

    def _build_ui(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=tk.X)

        self.title_label = ttk.Label(header, text=f"{self.session.name} on {self.session.port}")
        self.title_label.pack(side=tk.LEFT)

        ttk.Label(header, textvariable=self.status_var).pack(side=tk.RIGHT)

        body = ttk.Frame(self)
        body.pack(fill=tk.X, pady=(8, 0))

        self.sensor_frame = ttk.LabelFrame(body, text="Sensors", padding=8)
        self.sensor_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        output_frame = ttk.Frame(body)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(output_frame, text="CSV file:").pack(anchor=tk.W)

        file_row = ttk.Frame(output_frame)
        file_row.pack(fill=tk.X, pady=(4, 8))

        ttk.Entry(file_row, textvariable=self.output_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_row, text="Browse", command=self.browse_output_file).pack(side=tk.LEFT, padx=(6, 0))

        controls = ttk.Frame(output_frame)
        controls.pack(fill=tk.X)

        ttk.Button(controls, text="Start", command=self.start_recording).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(controls, text="Pause", command=self.pause_recording).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Stop", command=self.stop_recording).pack(side=tk.LEFT, padx=4)

        ttk.Label(controls, text="Timed length (s):").pack(side=tk.LEFT, padx=(16, 4))
        ttk.Entry(controls, textvariable=self.duration_var, width=8).pack(side=tk.LEFT)
        ttk.Button(controls, text="Start Timed", command=self.start_timed_recording).pack(side=tk.LEFT, padx=4)

    def refresh_device_info(self) -> None:
        self.config(text=f"{self.session.name} ({self.session.port})")
        self.title_label.config(text=f"{self.session.name} on {self.session.port}")

        if self.output_path_var.get().endswith(f"{self.session.port}.csv"):
            self.output_path_var.set(self._default_output_path())

        for child in self.sensor_frame.winfo_children():
            child.destroy()

        self.sensor_vars.clear()

        for sensor in self.session.sensors:
            var = tk.BooleanVar(value=True)
            self.sensor_vars[sensor.index] = var

            ttk.Checkbutton(
                self.sensor_frame,
                text=f"{sensor.index}: {sensor.name}",
                variable=var,
            ).pack(anchor=tk.W)

    def browse_output_file(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=Path(self.output_path_var.get()).name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if path:
            self.output_path_var.set(path)

    def selected_sensors(self) -> list[SensorInfo]:
        selected_indices = {index for index, var in self.sensor_vars.items() if var.get()}
        return [sensor for sensor in self.session.sensors if sensor.index in selected_indices]

    def start_recording(self) -> None:
        try:
            self.session.start(self.output_path_var.get(), self.selected_sensors())
            self.status_var.set("Recording")
            self.log_callback(f"[{self.session.port}] Recording started")
        except Exception as exc:
            messagebox.showerror("Start failed", str(exc))

    def pause_recording(self) -> None:
        try:
            self.session.pause()
            self.status_var.set("Paused")
            self.log_callback(f"[{self.session.port}] Recording paused")
        except Exception as exc:
            messagebox.showerror("Pause failed", str(exc))

    def stop_recording(self) -> None:
        try:
            self.session.stop()
            self.status_var.set("Stopped")
            self.log_callback(f"[{self.session.port}] Recording stopped")
        except Exception as exc:
            messagebox.showerror("Stop failed", str(exc))

    def start_timed_recording(self) -> None:
        try:
            duration = float(self.duration_var.get())
            self.session.start_timed(self.output_path_var.get(), self.selected_sensors(), duration)
            self.status_var.set(f"Timed recording: {duration:g} s")
            self.log_callback(f"[{self.session.port}] Timed recording started for {duration:g} s")
        except Exception as exc:
            messagebox.showerror("Timed start failed", str(exc))

    def write_sample_if_recording(self, sample) -> None:
        if self.session.recording and self.session.logger.is_open:
            self.session.logger.write_sample(sample)
