#pragma once

#include <Sensor.h>
#include <SensorConfigs.h>

class AnalogSensor : public Sensor
{
private:
    int pin;

public:
    explicit AnalogSensor(const AnalogSensorConfig &cfg);

    void begin() override;
    float sample() override;
};