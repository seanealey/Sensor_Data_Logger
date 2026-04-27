#pragma once

#include <Sensor.h>
#include <SensorConfigs.h>

class DigitalSensor : public Sensor
{
private:
    int pin;
    bool pulldown;

public:
    explicit DigitalSensor(const DigitalSensorConfig &cfg);

    void begin() override;
    float sample() override;
};