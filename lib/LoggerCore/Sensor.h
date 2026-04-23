#pragma once
#include <Arduino.h>

class Sensor
{
protected:
    const char *name;
    uint32_t sampleRateHz;
    uint32_t sampleIntervalUs;
    uint32_t lastSampleTimeUs = 0;
    bool recording = false;

public:
    Sensor(const char *sensorName, uint32_t rateHz)
        : name(sensorName), sampleRateHz(rateHz)
    {
        if (sampleRateHz == 0)
        {
            sampleRateHz = 1;
        }

        sampleIntervalUs = 1000000UL / sampleRateHz;
        if (sampleIntervalUs == 0)
        {
            sampleIntervalUs = 1;
        }
    }

    virtual ~Sensor() {}

    virtual void begin() = 0;
    virtual void sample() = 0;

    void startRecording()
    {
        recording = true;
        lastSampleTimeUs = micros();
    }

    void stopRecording()
    {
        recording = false;
    }

    bool isRecording() const
    {
        return recording;
    }

    const char *getName() const
    {
        return name;
    }

    uint32_t getSampleRateHz() const
    {
        return sampleRateHz;
    }

    void update()
    {
        if (!recording)
        {
            return;
        }

        uint32_t nowUs = micros();
        if ((uint32_t)(nowUs - lastSampleTimeUs) >= sampleIntervalUs)
        {
            lastSampleTimeUs += sampleIntervalUs;
            sample();
        }
    }
};