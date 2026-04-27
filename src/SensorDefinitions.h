#pragma once

#include <SensorConfigs.h>

static const AnalogSensorConfig analogSensors[] = {
    {"Potentiometer", 27, 100}

};

static const size_t analogSensorCount = sizeof(analogSensors) / sizeof(analogSensors[0]);

static const DigitalSensorConfig digitalSensors[] = {
    {"Button", 12, true, 100}

};

static const size_t digitalSensorCount = sizeof(digitalSensors) / sizeof(digitalSensors[0]);

static const HCSR04SensorConfig hcsr04Sensors[] = {
    {"Ultrasonic", 32, 33, 100}};

static const size_t hcsr04SensorCount = sizeof(hcsr04Sensors) / sizeof(hcsr04Sensors[0]);