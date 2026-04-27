#include "DigitalSensor.h"
#include <Arduino.h>

DigitalSensor::DigitalSensor(const DigitalSensorConfig &cfg)
    : Sensor(cfg.name, cfg.sampleRateHz), pin(cfg.pin), pullup(cfg.pullup) {}

void DigitalSensor::begin()
{
    pinMode(pin, INPUT);
    if (pullup)
    {
        pinMode(pin, INPUT_PULLDOWN);
    }
}

float DigitalSensor::sample()
{
    int value = digitalRead(pin);
    return static_cast<float>(value);
}