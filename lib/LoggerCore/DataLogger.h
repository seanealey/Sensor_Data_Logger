#pragma once

#include <Arduino.h>
#include <memory>
#include <vector>

#include "Sensor.h"
#include "SensorConfigs.h"

class DataLogger
{
private:
    String name;
    std::vector<std::unique_ptr<Sensor>> sensors;
    std::vector<Sensor *> testGroup;

public:
    DataLogger(const String &name);

    String getNodeInfo() const;

    int addSensor(const AnalogSensorConfig &cfg);
    // int addSensor(const HX711SensorConfig &cfg);

    Sensor *getSensor(size_t index);

    bool startSensor(size_t index);
    bool stopSensor(size_t index);

    void startAll();
    void stopAll();
    void update();

    void addToTestGroup(size_t index);
    void startTestGroup();
    void stopTestGroup();
    void updateTestGroup();

    size_t getSensorCount() const;
};