#include <Arduino.h>
#include <DataLogger.h>
#include "SensorDefinitions.h"
#include "SerialHandler.h"

DataLogger logger("Node1");
String pcComms; // variable to store incoming serial data for PC communication

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
  if (Serial.available() > 0)
  {
    String pcComms = Serial.readStringUntil('\n');
    pcComms.trim();

    if (pcComms.startsWith("HELLO"))
    {
      String info = logger.getNodeInfo();
      Serial.println(info);
    }
    else if (pcComms.startsWith("SELECT"))
    {
      std::vector<int> selectedIndices = HandleSelectCommand(pcComms);

      // logger.clearTestGroup(); // add this if you want new selection to replace old one

      for (int index : selectedIndices)
      {
        logger.addToTestGroup(index);
      }
    }
    else if (pcComms.startsWith("START"))
    {
      logger.startTestGroup();
    }
    else if (pcComms.startsWith("STOP"))
    {
      logger.stopTestGroup();
    }
  }

  logger.updateTestGroup();
}