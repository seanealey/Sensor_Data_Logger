#pragma once

#include <SensorConfigs.h>

static const AnalogSensorConfig analogSensors[] = {
    {"Potentiometer", 27, 1000}

};

static const size_t analogSensorCount = sizeof(analogSensors) / sizeof(analogSensors[0]);
