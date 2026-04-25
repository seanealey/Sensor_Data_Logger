#include "DataLogger.h"

#include <AnalogSensor.h>

DataLogger::DataLogger(const String &name) : name(name)
{
}

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

String DataLogger::getNodeInfo() const
{
    String msg;
    msg.reserve(64); // adjust if needed

    msg += "NODE,";
    msg += name;
    msg += ",SENSORS,";
    msg += sensors.size();

    for (const auto &sensor : sensors)
    {
        msg += ",";
        msg += sensor->getName();
    }

    return msg;
}

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

void DataLogger::addToTestGroup(size_t index)
{
    Sensor *sensor = getSensor(index);

    if (sensor == nullptr)
    {
        Serial.println("Invalid sensor index");
        return;
    }

    testGroup.push_back(sensor);
    Serial.print("Added sensor to test group: ");
    Serial.println(sensor->getName());
}
Sensor *DataLogger::getSensor(size_t index)
{
    if (index >= sensors.size())
    {
        return nullptr;
    }

    return sensors[index].get();
}

void DataLogger::startTestGroup()
{
    for (auto &sensor : testGroup)
    {
        sensor->startRecording();
    }
}

void DataLogger::stopTestGroup()
{
    for (auto &sensor : testGroup)
    {
        sensor->stopRecording();
    }
}

void DataLogger::updateTestGroup()
{
    std::vector<float> samples;
    for (auto &sensor : testGroup)
    {
        if (sensor->isRecording())
        {
            float sampleValue = sensor->update();
            samples.push_back(sampleValue);
        }
    }

    if (!samples.empty())
    {
        Serial.print("DATA");
        for (float sample : samples)
        {
            Serial.print(",");
            Serial.print(sample);
        }
        Serial.println();
    }
}

size_t DataLogger::getSensorCount() const
{
    return sensors.size();
}