# RoboAide

## Description
RoboAide is a project to improve a DIY robotic arm used for mobility assistance. This repository contains code for a GUI application as well as Arduino code for the control of the arm's motors. The application is made in Python using PySide2 and communicates the desired motor positions via USB serial communication with the Arduio/OpenCR board.

## Instructions
1. Install all dependencies
2. Plug in the OpenCR board to the pc via USB and find the the right communication port
3. Upload the Arduino code
3. Run RoboAide.py with python to launch the GUI application

## Dependencies
* PySide2
* PySerial
* OpenCR board support for Arduino IDE
