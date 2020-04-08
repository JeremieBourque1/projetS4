# RoboAide

[![Build Status](https://travis-ci.com/JeremieBourque1/projetS4.svg?branch=master)](https://travis-ci.com/JeremieBourque1/projetS4)

## Description
RoboAide is a project to improve a DIY robotic arm used for mobility assistance. This repository contains code for a GUI application as well as Arduino code for the control of the arm's motors. The application is made in Python using PySide2 and communicates the desired motor positions via USB serial communication with the Arduio/OpenCR board.
*NOTE*: follow the instructions section before launching the application.

## Overview of the application

The application is written in Python and is designed to run on Windows but should also run on other platforms, although this was not tested extensively.
The application contains three tabs: "Motor control", which is for moving the arm's motors individually in joint mode, "Sequences", which is for creating move sequences and executing them, and "Drawers", which is for opening and closing drawers.

### Motor control
![Image of the motor control tab](https://github.com/JeremieBourque1/projetS4/blob/master/images/ui_motorControl.jpg)
To start the connection, select the appropriate communication port in the drop-down menu. Once connected, moving the sliders will move the motors.

### Sequences
![Image of the sequences tab](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/ui_seq.jpg)
Here, you can see the list of user-created sequences. To execute a sequence, double click the sequence.
![Image of the new sequence window](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/ui_newSeq.jpg)
To create a new sequence, click the "Create new sequence" button, which will open this window. You can move the sliders to the desired position, then click "Save move" and create the next move. Double clicking a saved move will move the arm to that position. When done, click "ok".

### Drawers
![Image of the drawers tab](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/ui_drawers.jpg)
This tab makes it possible to open and close the drawers. Note that this feature is not yet implemented in the controller, so the buttons currently do nothing. The feature will be implemented in a future version.


## Hardware Requirements
* PC running Windows (may also run on other platforms, but hasn't been testes)
* OpenCR board
* Dynamixel motors
* TODO: VERTICAL AXIS REQUIREMENTS

## Software requirements

### UI Dependencies
* Python 3.7 or later (https://www.python.org/downloads/)
* PySide2 
* PySerial

The necessary Pyton libraries can be installed with `pip install -r requirements.txt`

### Controller dependencies
* Arduino IDE (https://www.arduino.cc/en/main/software)
* OpenCR diver (should install automatically when the board is plugged into the PC
* OpenCR board support for Arduino IDE (http://emanual.robotis.com/docs/en/parts/controller/opencr10/#install-on-windows)

## Instructions
1. Install all dependencies
2. Plug in the OpenCR board to the PC via USB
3. Launch Arduino IDE and choose the right board and communication port.
4. Upload the Arduino code
5. Run RoboAide.py with python to launch the GUI application. To do this, open a command prompt, change the directory to this project's directory and run this command `python UI/RoboAide.py`


## Software documentation
All software documentation can be viewed [here](https://jeremiebourque1.github.io/projetS4/)


## Hardware documentation
TODO

## Unit tests
The application is tested using the unittest python module. To run the tests, open a command prompt, change the directory to the project’s directory and run this command: `python -m unittest discover`

