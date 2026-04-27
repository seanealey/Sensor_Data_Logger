#include "DigitalSensor.h"
#include <Arduino.h>

DigitalSensor::DigitalSensor(const DigitalSensorConfig &cfg)
    : Sensor(cfg.name, cfg.sampleRateHz), pin(cfg.pin), pulldown(cfg.pulldown) {}

void DigitalSensor::begin()
{
    pinMode(pin, INPUT);
    if (pulldown)
    {
        pinMode(pin, INPUT_PULLDOWN);
    }
}

float DigitalSensor::sample()
{
    int value = digitalRead(pin);
    return static_cast<float>(value);
}