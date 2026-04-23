#include "DataLogger.h"

#include <AnalogSensor.h>

int DataLogger::addSensor(const AnalogSensorConfig &cfg)
{
    auto sensor = std::make_unique<AnalogSensor>(cfg);
    sensor->begin();
    sensors.push_back(std::move(sensor));
    return (int)(sensors.size() - 1);
}

/*
int DataLogger::addSensor(const HX711SensorConfig &cfg)
{
    auto sensor = std::make_unique<HX711Sensor>(cfg);
    sensor->begin();
    sensors.push_back(std::move(sensor));
    return (int)(sensors.size() - 1);
}

*/
bool DataLogger::startSensor(size_t index)
{
    if (index >= sensors.size())
    {
        return false;
    }

    sensors[index]->startRecording();
    return true;
}

bool DataLogger::stopSensor(size_t index)
{
    if (index >= sensors.size())
    {
        return false;
    }

    sensors[index]->stopRecording();
    return true;
}

void DataLogger::startAll()
{
    for (auto &sensor : sensors)
    {
        sensor->startRecording();
    }
}

void DataLogger::stopAll()
{
    for (auto &sensor : sensors)
    {
        sensor->stopRecording();
    }
}

void DataLogger::update()
{
    for (auto &sensor : sensors)
    {
        sensor->update();
    }
}

size_t DataLogger::getSensorCount() const
{
    return sensors.size();
}