#pragma once
#include <Arduino.h>
#include <memory>
#include <vector>

#include "Sensor.h"
#include "SensorConfigs.h"

class DataLogger
{
private:
    std::vector<std::unique_ptr<Sensor>> sensors;

public:
    int addSensor(const AnalogSensorConfig &cfg);
    // int addSensor(const HX711SensorConfig &cfg);

    bool startSensor(size_t index);
    bool stopSensor(size_t index);

    void startAll();
    void stopAll();
    void update();

    size_t getSensorCount() const;
};