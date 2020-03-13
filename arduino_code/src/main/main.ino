#include <Arduino.h>
//#include "dynamixel.h"
#include "axialMotor.h"

// Declare constants
const int MESSAGE_SIZE = 13;
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
  //! Motor 1 position
  uint16_t p1;
  //! Motor 2 position
  uint16_t p2;
  //! Motor 3 position
  uint16_t p3;
  //! Motor 4 position
  uint16_t p4;
  //! Motor 5 position
  uint16_t p5;
  //! Motor 6 position
  uint16_t p6;
  //! End of message character
  char last;
};

// Function prototypes
bool readDataToStruct(dataPack *data);
void readMessage(char *message);
void sendMessage(dataPack message);
bool shouldSlowDown(int motorDirection);
bool runAxialCalibration(int motorDirection, int* motor);
bool setAxialMotorDirection(int directionValue, int* motor);
bool checkAxialMotorDirection(int directionValue, int* motor);
//axialMotor axialMotor(13,-1,47,49,51,53);
axialMotor test; //classe test

// Arduino functions
void setup() {
  Serial.begin(9600); // set the baud rate, must be the same for both machines
  while (!Serial);
//  mot1.init();
//  mot2.init();
//  mot3.init();
//  dataPack outgoingMessage{(int32_t)(mot1.getPosition()), (int32_t)(mot2.getPosition()), (int32_t)(mot3.getPosition()), 0, 0, 0};
//  sendMessage(outgoingMessage);
  pinMode(test.getProximitySensorPin(1), INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  pinMode(test.getProximitySensorPin(2), INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  pinMode(test.getMotorPin(1),OUTPUT);
  pinMode(test.getMotorPin(2),OUTPUT);
  pinMode(test.getDrivePin(),OUTPUT);
}

void loop() {
  test.setEnableDrive(true);
  //test.setMotorState(-1);
  test.runAxialCalibration();
  Serial.println("done");
  while (1)
  //{Serial.print(test.getProximitySensorValue(1));}
  if (Serial.available() >= MESSAGE_SIZE) // Only parse message when the full message has been received.
  {
    // Read data
    dataPack data;
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


      // TODO: Call move motor functinons
//      mot1.moveMotor(data.p1);
//      mot2.moveMotor(data.p2);
//      mot3.moveMotor(data.p3);

//      dataPack outgoingMessage{(int32_t)(mot1.getPosition()), (int32_t)(mot2.getPosition()), (int32_t)(mot3.getPosition()), 0, 0, 0};
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
