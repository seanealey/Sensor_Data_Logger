#include <Arduino.h>
#include <DataLogger.h>
#include "SensorDefinitions.h"

DataLogger logger;

void setup()
{
  Serial.begin(115200);

  for (size_t i = 0; i < analogSensorCount; i++)
  {
    logger.addSensor(analogSensors[i]);
  }

  logger.startAll();
}

void loop()
{
  logger.update();
}