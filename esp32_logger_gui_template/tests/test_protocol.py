from esp32_logger_gui.protocol import build_config_command, parse_data_sample, parse_sensors


def test_parse_sensors():
    sensors = parse_sensors("SENSORS,0:load_cell,1:encoder")
    assert sensors is not None
    assert sensors[0].index == 0
    assert sensors[0].name == "load_cell"


def test_parse_data_sample():
    sample = parse_data_sample("DATA,123,1,45.6")
    assert sample is not None
    assert sample.time_ms == 123
    assert sample.sensor_index == 1
    assert sample.value == 45.6


def test_build_config_command():
    assert build_config_command([0, 2, 3]) == "CONFIG,0,2,3"
