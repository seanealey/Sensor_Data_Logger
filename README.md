This is a sensor data logging project That makes it easy to collect sensor data using an arduino/esp device. Drivers can be written for individual sensor types then configured in the sensor definitions header file. once logger is initialised all sensors declared will be automatically added. from there recording can be started, stopped for individual sensors or all at the same time.

to activate virtual environment for python scrip use the following command in the logger_gui folder

.\.venv\Scripts\Activate.ps1

then run logger_gui command to open the gui


TODO:

test multi sensors on one board
expand support for multiple boards at a time
get timestamp from device instead of pc
add csv folder
fix pause option
fix timer option
add pause function to esp
