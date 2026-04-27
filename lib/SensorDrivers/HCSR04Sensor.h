#pragma once

#include <Sensor.h>
#include <SensorConfigs.h>

// HC-SR04 Ultrasonic Sensor Driver

class HCSR04Sensor : public Sensor
{
private:
    int triggerPin;
    int echoPin;

public:
    explicit HCSR04Sensor(const HCSR04SensorConfig &cfg);

    void begin() override;
    float sample() override;
};