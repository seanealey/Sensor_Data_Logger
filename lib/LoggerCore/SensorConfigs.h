#pragma once
#include <Arduino.h>

struct AnalogSensorConfig
{
    const char *name;
    int pin;
    uint32_t sampleRateHz;
};

struct DigitalSensorConfig
{
    const char *name;
    int pin;
    bool pullup; // true for INPUT_PULLUP, false for INPUT
    uint32_t sampleRateHz;
};

struct HCSR04SensorConfig
{
    const char *name;
    int echoPin;
    int triggerPin;
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