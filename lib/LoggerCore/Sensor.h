#pragma once
#include <Arduino.h>

class Sensor
{
protected:
    const char *name;
    uint32_t sampleRateHz;
    uint32_t sampleIntervalUs;
    uint32_t lastSampleTimeUs = 0;
    float sampleValue = 0.0f;
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
    virtual float sample() = 0;

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

    float update(uint32_t currentTimeUs, uint32_t lastUpdateTimeUs)
    {

                if ((uint32_t)(currentTimeUs - lastSampleTimeUs) >= sampleIntervalUs)
        {
            lastSampleTimeUs += sampleIntervalUs;
            sampleValue = sample();
        }

        return sampleValue;
    }
};