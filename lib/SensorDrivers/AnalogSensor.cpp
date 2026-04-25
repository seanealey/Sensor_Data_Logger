#include "AnalogSensor.h"
#include <Arduino.h>

AnalogSensor::AnalogSensor(const AnalogSensorConfig &cfg)
    : Sensor(cfg.name, cfg.sampleRateHz), pin(cfg.pin) {}

void AnalogSensor::begin()
{
    pinMode(pin, INPUT);
}

float AnalogSensor::sample()
{
    int value = analogRead(pin);
    return static_cast<float>(value);
}