#include "SerialHandler.h"

std::vector<int> HandleSelectCommand(String line)
{
    std::vector<int> selectedIndices;
    line.trim(); // remove \n, \r, spaces

    if (!line.startsWith("SELECT"))
        return selectedIndices;

    // Example: "Select, 0, 2"
    int firstComma = line.indexOf(',');
    if (firstComma == -1)
        return selectedIndices;

    String indicesPart = line.substring(firstComma + 1);
    indicesPart.trim();

    // Parse indices separated by commas
    while (indicesPart.length() > 0)
    {
        int commaIndex = indicesPart.indexOf(',');

        String token;
        if (commaIndex == -1)
        {
            token = indicesPart;
            indicesPart = "";
        }
        else
        {
            token = indicesPart.substring(0, commaIndex);
            indicesPart = indicesPart.substring(commaIndex + 1);
        }

        token.trim();
        int index = token.toInt();

        selectedIndices.push_back(index);
    }
    return selectedIndices;
}