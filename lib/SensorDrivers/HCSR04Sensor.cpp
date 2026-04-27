#include "HCSR04Sensor.h"
#include <Arduino.h>

HCSR04Sensor::HCSR04Sensor(const HCSR04SensorConfig &cfg)
    : Sensor(cfg.name, cfg.sampleRateHz), triggerPin(cfg.triggerPin), echoPin(cfg.echoPin) {}

void HCSR04Sensor::begin()
{
    pinMode(triggerPin, OUTPUT);
    pinMode(echoPin, INPUT);
}

float HCSR04Sensor::sample()
{

    digitalWrite(triggerPin, LOW);
    delayMicroseconds(2);
    digitalWrite(triggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(triggerPin, LOW);

    long duration = pulseIn(echoPin, HIGH);
    float distance = duration * 0.0343 / 2;
    return distance;
}