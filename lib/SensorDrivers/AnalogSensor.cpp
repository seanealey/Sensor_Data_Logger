#include "AnalogSensor.h"
#include <Arduino.h>

AnalogSensor::AnalogSensor(const AnalogSensorConfig &cfg)
    : Sensor(cfg.name, cfg.sampleRateHz), pin(cfg.pin) {}

void AnalogSensor::begin()
{
    pinMode(pin, INPUT);
}

void AnalogSensor::sample()
{
    int value = analogRead(pin);

    Serial.print(name);
    Serial.print(",");
    Serial.println(value);
}