from __future__ import annotations

import queue
import tkinter as tk
from tkinter import messagebox, ttk

from logger_gui.device_panel import DevicePanel
from logger_gui.device_session import DeviceSession
from logger_gui.protocol import parse_data_sample, parse_device_and_sensors
from logger_gui.serial_interface import SerialConnection, list_serial_devices


class LoggerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Logger GUI")
        self.geometry("1000x650")

        self.incoming_lines: queue.Queue[tuple[str, str]] = queue.Queue()
        self.sessions: dict[str, DeviceSession] = {}
        self.panels: dict[str, DevicePanel] = {}
        self._ports = []

        self._build_ui()
        self.refresh_ports()
        self.after(50, self._process_incoming_lines)

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        top = ttk.LabelFrame(main, text="Devices", padding=10)
        top.pack(fill=tk.X)

        self.port_combo = ttk.Combobox(top, state="readonly", width=45)
        self.port_combo.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(top, text="Refresh", command=self.refresh_ports).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Connect Selected", command=self.connect_selected_port).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Connect All", command=self.connect_all_ports).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Disconnect All", command=self.disconnect_all).pack(side=tk.LEFT, padx=4)

        self.device_count_label = ttk.Label(top, text="No devices connected")
        self.device_count_label.pack(side=tk.LEFT, padx=16)

        self.devices_container = ttk.LabelFrame(main, text="Connected Devices", padding=10)
        self.devices_container.pack(fill=tk.BOTH, expand=True, pady=10)

        self.devices_canvas = tk.Canvas(self.devices_container, highlightthickness=0)
        self.devices_scrollbar = ttk.Scrollbar(
            self.devices_container,
            orient=tk.VERTICAL,
            command=self.devices_canvas.yview,
        )
        self.devices_frame = ttk.Frame(self.devices_canvas)

        self.devices_frame.bind(
            "<Configure>",
            lambda event: self.devices_canvas.configure(scrollregion=self.devices_canvas.bbox("all")),
        )

        self.devices_canvas.create_window((0, 0), window=self.devices_frame, anchor="nw")
        self.devices_canvas.configure(yscrollcommand=self.devices_scrollbar.set)

        self.devices_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.devices_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        log_box = ttk.LabelFrame(main, text="Serial Log", padding=10)
        log_box.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        self.log_text = tk.Text(log_box, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def refresh_ports(self) -> None:
        devices = list_serial_devices()
        self._ports = devices

        connected_ports = set(self.sessions.keys())
        values = [
            f"{device.port} | {device.description}"
            for device in devices
            if device.port not in connected_ports
        ]

        self.port_combo["values"] = values
        self._available_ports = [device for device in devices if device.port not in connected_ports]

        if values:
            self.port_combo.current(0)
        else:
            self.port_combo.set("")

    def connect_selected_port(self) -> None:
        selected_index = self.port_combo.current()
        if selected_index < 0:
            messagebox.showwarning("No port selected", "Select a serial port first.")
            return

        device = self._available_ports[selected_index]
        self._connect_port(device.port)
        self.refresh_ports()

    def connect_all_ports(self) -> None:
        for device in list(getattr(self, "_available_ports", [])):
            self._connect_port(device.port, show_errors=False)

        self.refresh_ports()

    def _connect_port(self, port: str, show_errors: bool = True) -> None:
        if port in self.sessions:
            return

        try:
            connection = SerialConnection(port)
            connection.connect()
            connection.start_reader(lambda line, port=port: self.incoming_lines.put((port, line)))

            session = DeviceSession(port, connection)
            self.sessions[port] = session

            session.send("HELLO")
            self._log(f"[{port}] > HELLO")
            self._log(f"[{port}] Connected")
            self._update_device_count()

        except Exception as exc:
            if show_errors:
                messagebox.showerror("Connection failed", f"{port}: {exc}")
            self._log(f"[{port}] Connection failed: {exc}")

    def disconnect_all(self) -> None:
        for port in list(self.sessions.keys()):
            self.disconnect_device(port)

    def disconnect_device(self, port: str) -> None:
        session = self.sessions.pop(port, None)
        if not session:
            return

        try:
            session.disconnect()
        except Exception as exc:
            self._log(f"[{port}] Disconnect error: {exc}")

        panel = self.panels.pop(port, None)
        if panel:
            panel.destroy()

        self._log(f"[{port}] Disconnected")
        self._update_device_count()
        self.refresh_ports()

    def _process_incoming_lines(self) -> None:
        while not self.incoming_lines.empty():
            port, line = self.incoming_lines.get()
            self._handle_line(port, line)

        self.after(50, self._process_incoming_lines)

    def _handle_line(self, port: str, line: str) -> None:
        self._log(f"[{port}] {line}")

        session = self.sessions.get(port)
        if not session:
            return

        result = parse_device_and_sensors(line)
        if result:
            device_name, sensors = result
            session.set_device_info(device_name, sensors)
            self._create_or_update_panel(session)
            self._update_device_count()
            return

        sample = parse_data_sample(line)
        if sample is not None and session.recording and session.logger.is_open:
            session.logger.write_sample(sample)

    def _create_or_update_panel(self, session: DeviceSession) -> None:
        panel = self.panels.get(session.port)

        if panel is None:
            panel = DevicePanel(self.devices_frame, session, self._log)
            panel.pack(fill=tk.X, pady=6)
            self.panels[session.port] = panel
        else:
            panel.refresh_device_info()

    def _update_device_count(self) -> None:
        count = len(self.sessions)
        if count == 0:
            self.device_count_label.config(text="No devices connected")
        elif count == 1:
            self.device_count_label.config(text="1 device connected")
        else:
            self.device_count_label.config(text=f"{count} devices connected")

    def _log(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def destroy(self) -> None:
        self.disconnect_all()
        super().destroy()
