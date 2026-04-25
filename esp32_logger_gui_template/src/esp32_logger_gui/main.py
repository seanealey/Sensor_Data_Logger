from esp32_logger_gui.gui.app import LoggerApp


def main() -> None:
    app = LoggerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
