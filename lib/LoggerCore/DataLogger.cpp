#include "DataLogger.h"

#include <AnalogSensor.h>
#include <DigitalSensor.h>
#include <HCSR04Sensor.h>

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

int DataLogger::addSensor(const DigitalSensorConfig &cfg)
{
    auto sensor = std::make_unique<DigitalSensor>(cfg);
    sensor->begin();
    sensors.push_back(std::move(sensor));
    return (int)(sensors.size() - 1);
}

int DataLogger::addSensor(const HCSR04SensorConfig &cfg)
{
    auto sensor = std::make_unique<HCSR04Sensor>(cfg);
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
        sensor->update(CurrentTimeUs, LastUpdateTimeUs);
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
    TestStartTimeUs = micros();
    LastUpdateTimeUs = 0;
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
        testGroup.clear(); // Clear the test group after stopping
    }
}

void DataLogger::updateTestGroup()
{
    CurrentTimeUs = micros() - TestStartTimeUs;
    std::vector<float> samples;
    samples.push_back((float)CurrentTimeUs);

    for (auto &sensor : testGroup)
    {
        if (sensor->isRecording())
        {
            float sampleValue = sensor->update(CurrentTimeUs, LastUpdateTimeUs);
            samples.push_back(sampleValue);
        }
    }

    if (!samples.empty() && samples.size() > 1) // Ensure we have at least one sensor sample to send
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

void DataLogger::clearTestGroup()
{
    testGroup.clear();
    Serial.println("Test group cleared");
}

size_t DataLogger::getSensorCount() const
{
    return sensors.size();
}