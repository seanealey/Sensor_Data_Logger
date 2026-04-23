#pragma once
#include <Arduino.h>

struct AnalogSensorConfig
{
    const char *name;
    int pin;
    uint32_t sampleRateHz;
};

/*
struct HX711SensorConfig
{
    const char *name;
    int doutPin;
    int sckPin;
    uint32_t sampleRateHz;
    float calibrationFactor;
};

*/