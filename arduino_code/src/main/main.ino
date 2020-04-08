#include <Arduino.h>
//#include "dynamixel.h"
#include "axialMotor.h"

// Declare global variables
const int MESSAGE_SIZE = 19;
char endOfMessageChar = '\0';
const int id3 = 221;
const int id1 = 222;
const int id2 = 223;
//Dynamixel mot1(id1, 28);
//Dynamixel mot2(id2, 40);
//Dynamixel mot3(id3, 20);


/**
   \struct dataPack
   \brief A structure containing message data
*/
struct dataPack {
  //! Operation mode
  char mode;
  //! Motor 1 position
  uint16_t p1;
  //! Motor 2 position
  uint16_t p2;
  //! Motor 3 position
  uint16_t p3;
  //! Motor 4 position
  uint16_t p4; // Vertical motor
  //! Motor 5 position
  uint16_t p5;
  //! Motor 6 position
  uint16_t p6;
  //! Stop indicator
  bool shouldStop;
  //! Drawer 1 state
  bool drawer1;
  //! Drawer 2 state
  bool drawer2;
  //! Drawer 3 state
  bool drawer3;
  //! End of message character
  char last;
};

// Function prototypes
bool readDataToStruct(dataPack *data);
void readMessage(char *message);
void sendMessage(dataPack message);
void moveAbsolute(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6);
void moveIncremental(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6);
void setDrawerGoalState(bool drawer1, bool drawer2, bool drawer3);
void stopMotors();
void startMotors();

void trigShouldSlowDownPin1();
void trigShouldSlowDownPin2();

//axialMotor axialMotor(53,-1,A1,A2,19,20,2,3);
axialMotor test; //classe test

// Arduino functions
void setup() {
  Serial.begin(9600); // set the baud rate, must be the same for both machines
  //while (!Serial);
//  mot1.init();
//  mot2.init();
//  mot3.init();
  //dataPack outgoingMessage{(byte)'s',(int32_t)(mot1.getPosition()), (int32_t)(mot2.getPosition()), (int32_t)(mot3.getPosition()), 0, 0, 0, (byte)'\0'};
  //sendMessage(outgoingMessage);
  pinMode(test.getProximitySensorPin(1), INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  pinMode(test.getProximitySensorPin(2), INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  attachInterrupt(digitalPinToInterrupt(test.getProximitySensorPin(1)), trigShouldSlowDownPin1, FALLING);
  attachInterrupt(digitalPinToInterrupt(test.getProximitySensorPin(2)), trigShouldSlowDownPin2, FALLING);
  pinMode(test.getMotorPin(1),OUTPUT);
  pinMode(test.getMotorPin(2),OUTPUT);
  pinMode(test.getDrivePin(),OUTPUT);

  pinMode(38,OUTPUT); //power for one of the sensor
  digitalWrite(38,HIGH); //power for one of the sensor
  test.setEnableDrive(true);
  test.modifyCalibrationCase(-2);
  test.setMotorState(0);
}
bool buttonCalibration = false;
int requiredPosition = 2000;
bool slowItTOP = false;
bool slowItBOT = false;

void loop() {

  long encPosition = test.enc->read();
  
  test.runIt(encPosition,&slowItTOP,&slowItBOT,requiredPosition,buttonCalibration);


  if (Serial.available() >= MESSAGE_SIZE) // Only parse message when the full message has been received.
  {
    // Read data
    dataPack data;
   // test.runIt(encPosition,&slowItTOP,&slowItBOT,data.p4,data.buttonCalibration);
    if (readDataToStruct(&data))
    {
      // Debug
      //Serial.println(data.p1);
      //Serial.println(data.p2);
      //Serial.println(data.p3);
      //Serial.println(data.p4);
      //Serial.println(data.p5);
      //Serial.println(data.p6);
      //Serial.println(data.end);
      //byte* serializedMessage = (byte*)&data, sizeof(data);
      //Serial.println(serializedMessage);
      if(data.shouldStop == false)
      {
        if(data.mode == 'a')
        {
          moveAbsolute(data.p1, data.p2, data.p3, data.p4, data.p5, data.p6);
          setDrawerGoalState(data.drawer1, data.drawer2, data.drawer3);
        }
        else if(data.mode == 'i')
        {
          moveIncremental(data.p1, data.p2, data.p3, data.p4, data.p5, data.p6);
          setDrawerGoalState(data.drawer1, data.drawer2, data.drawer3);
        }
        else if(data.mode == 's')
        {
          // Do nothing apart from sending message
        }
        else if(data.mode == 'c')
        {
          //TODO: connect to calibration function
        }
      }
      else
      {
        stopMotors();
        startMotors();
      }


      // TODO: Call move motor functinons
//      mot1.moveMotor(data.p1);
//      mot2.moveMotor(data.p2);
//      mot3.moveMotor(data.p3);

//      dataPack outgoingMessage{(byte)'a', (int32_t)(mot1.getPosition()), (int32_t)(mot2.getPosition()), (int32_t)(mot3.getPosition()), 0, 0, 0, (bool)data.shouldStop, (byte)'\0'};
//      sendMessage(outgoingMessage);
    }
    else
    {
      //Serial.println("Failed to parse message");
    }
  }
}

// Functions

/** \brief Iterates through message one character at a time until the end character is found and returns a char array of the message.
    \param message : empty character array
    \return message : character array containing message
*/
void readMessage(char *message)
{
  int count = 0;
  char c;

  do
  {
    if (Serial.available())
    {
      c = Serial.read();
      message[count] = c;
      count++;
    }
  } while (c != '\0');
}


/** \brief Iterates through message one byte at a time casts it to a dataPack struct.
    \param data : empty dataPack object the message will be written to
    \return data : dataPack object containging the unpacked message data
*/
bool readDataToStruct(dataPack *data)
{
  int i = 0;
  byte buf[MESSAGE_SIZE];
  while (Serial.available() && i < MESSAGE_SIZE)
  {
    buf[i] = Serial.read();
    i++;
  }
  memcpy(data, buf, sizeof(*data));
  if (data->last != endOfMessageChar) // if the last character is not the end-of-message character, message is corrupted
    return false;

  return true;
}


/** \brief Sends an encoded message over serial
    \param message : empty dataPack object the message will be written to
*/
void sendMessage(dataPack message)
{
  Serial.write((byte*)&message, sizeof(message));
}


/** \brief move motors to an absolute position
    \param p1, ..., p6 : position for each motor
*/
void moveAbsolute(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6)
{
//    mot1.moveMotor(p1);
//    mot2.moveMotor(p2);
//    mot3.moveMotor(p3);
}

/** \brief move motors to an incremental position
    \param p1, ..., p6 : position for each motor
*/
void moveIncremental(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6)
{
  //TODO
}

void setDrawerGoalState(bool drawer1, bool drawer2, bool drawer3)
{
  //TODO
}

void stopMotors()
{
//  mot1.torque(false);
//  mot2.torque(false);
//  mot3.torque(false);
}

void startMotors()
{
//  mot1.torque(true);
//  mot2.torque(true);
//  mot3.torque(true);
} 

void trigShouldSlowDownPin1()
{
    slowItTOP = true;
    if(test.shouldSlowDown(slowItTOP,slowItBOT) == true)
    {
      test.setMotorState(-1);
    }
}

void trigShouldSlowDownPin2()
{
  slowItBOT = true;

  if(test.shouldSlowDown(slowItTOP,slowItBOT) == true)
  {
    test.setMotorState(-1);
  }
}
