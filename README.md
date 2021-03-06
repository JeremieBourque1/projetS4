# RoboAide

[![Build Status](https://travis-ci.com/JeremieBourque1/projetS4.svg?branch=master)](https://travis-ci.com/JeremieBourque1/projetS4)


## Description
RoboAide is a project to improve a DIY robotic arm used for mobility assistance. This repository contains code for a GUI application, Arduino code for the control of the arm's motors as well as CAD parts for a 3D printed shell for the arm segments and joints. The application is made in Python using PySide2 and communicates the desired motor positions via USB serial communication with the Arduio/OpenCR board.<br/>
Due to the team's limitation in regards to access to the robotic arm, a smaller prototype version of the arm was built and it was with it that the software was written and tested on. However, the 3D printed shell was designed for the actual arm. In a future version, the software will be adapted for the real arm as well.

![Image of arm prototype and GUI app](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/arm_and_gui.jpg)

## Overview of the application

The application is written in Python and is designed to run on Windows but should also run on other platforms, although this was not tested extensively.
The application contains three tabs: "Motor control", which is for moving the arm's motors individually in joint mode, "Sequences", which is for creating move sequences and executing them, and "Drawers", which is for opening and closing drawers.
It is to be noted that the code controlling the arm is split into two parts.The first is in the main and runs the openCR code for all of the arm's movements. The second is in the Vertical_Axis branch and runs the arduino code which moves the vertical motor.


*NOTE*: follow the instructions section before launching the application.

### Motor control
![Image of the motor control tab](https://github.com/JeremieBourque1/projetS4/blob/master/images/ui_motorControl.jpg)<br/>
To start the connection, select the appropriate communication port in the drop-down menu. Once connected, moving the sliders will move the motors.

### Sequences
![Image of the sequences tab](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/ui_seq.jpg)<br/>
Here, you can see the list of user-created sequences. To execute a sequence, double click the sequence.<br/><br/>
![Image of the new sequence window](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/ui_newSeq.jpg)<br/>
To create a new sequence, click the "Create new sequence" button, which will open this window. You can move the sliders to the desired position, then click "Save move" and create the next move. Double clicking a saved move will move the arm to that position. When done, click "ok".

### Drawers
![Image of the drawers tab](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/ui_drawers.jpg)<br/>
This tab makes it possible to open and close the drawers. Note that this feature is not yet implemented in the controller, so the buttons currently do nothing. The feature will be implemented in a future version.

## Hardware Requirements
* 1x PC running Windows (may also run on other platforms, but hasn't been tested)
* 1x OpenCR board
* 3x Dynamixel motors
* 2x Twidec NJK-5002J inductive proximity sensor
* 1x L298N DC motor drive
* 1x Cytron 12v DC motor
* Robot arm prototype (see hardware documentation for more information)

## Software requirements

### UI Dependencies
* Python 3.7 or later (https://www.python.org/downloads/)
* pip (https://www.liquidweb.com/kb/install-pip-windows/)
* PySide2 
* PySerial

The necessary Python libraries can be installed with `pip install -r requirements.txt`

### Controller dependencies
* Arduino IDE (https://www.arduino.cc/en/main/software)
* OpenCR driver (should install automatically when the board is plugged into the PC)
* OpenCR board support for Arduino IDE (http://emanual.robotis.com/docs/en/parts/controller/opencr10/#install-on-windows)

## Instructions for the robot arm
1. Install all dependencies
2. Plug in the OpenCR board to the PC via USB
3. Launch Arduino IDE and choose the right board and communication port.
4. Upload the Arduino code
5. Run RoboAide.py with python to launch the GUI application. To do this, open a command prompt, change the directory to this project's directory and run this command `python UI/RoboAide.py`

## Instruction for the vertical axis
1. Plug all electronic according to the wiring diagram (see below)
2. Once plugged in, run and push the main.ino code which is under the Arduino_code folder to your arduino.
3. Open Pycharm and run the RoboAide.py file which can be found under the ui folder.
4. An application should pop up. Choose your communication port on the application and wait for 10 seconds to let the arduino initialise its comm port.
5. The vertical axis is ready to be calibrated. Press "calibrate vertical axis" button. Once the robot arm has been calibrated, you're free to use the 
slider #4 to move the vertical axis.

## Software documentation
All software documentation can be viewed [here](https://jeremiebourque1.github.io/projetS4/)

## Hardware documentation
### Robotic arm prototype
*The bill of materials for the robot arm prototype can be viewed [here](https://github.com/JeremieBourque1/projetS4/blob/master/BOM_proto.xlsx?raw=true)
* OpenCR documentation can be viewed [here](https://github.com/JeremieBourque1/projetS4/blob/master/electronic/OpenCR/robotis-opencr10-cortex-microcontroller-ros-datasheet.pdf)
* Electrical diagram of the prototype

![Image of the electrical diagram](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/electrical_diagram.png)
### Robotic arm shell
Everything concerning the arm shell can be found [here](https://github.com/JeremieBourque1/projetS4/tree/master/Arm%20Shell)
### Vertical axis
* DC driver L298N documentation can be viewed [here](https://github.com/JeremieBourque1/projetS4/blob/master/electronic/DC%20motor%20drive/L298N%20Motor%20Driver.pdf)
* Twidec NJK-5002J Inductive limit switch documentation can be viewed [here](https://github.com/JeremieBourque1/projetS4/blob/master/electronic/Limit%20switch/Twidec%20NJK-5002C%20SpecSheet.pdf)
* Cytron 12v DC motor documentation can be viewed [here](https://github.com/JeremieBourque1/projetS4/tree/master/electronic/Cytron%20DC%20motor)
* For wiring images using arduino mega2560 : 

![Image of the wiring](https://raw.githubusercontent.com/JeremieBourque1/projetS4/master/images/arduino%20montage.png)

## Unit tests
The application is tested using the unittest python module. To run the tests, open a command prompt, change the directory to the project’s directory and run this command: `python -m unittest discover`

