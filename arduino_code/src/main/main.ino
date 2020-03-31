#include <Arduino.h>
#include "dynamixel.h"
#include "axialMotor.h"
// We used those links to modify encoder.cpp
//https://github.com/ROBOTIS-GIT/OpenCM9.04/pull/30/files
//http://emanual.robotis.com/docs/en/parts/controller/opencr10/#layoutpin-map
#include "encoder/Encoder.cpp"

// Declare constants
const int MESSAGE_SIZE = 15;
char endOfMessageChar = '\0';
const int id3 = 221;
const int id1 = 222;
const int id2 = 223;
Dynamixel mot1(id1, 0.879); //28
Dynamixel mot2(id2, 0.879); //40
Dynamixel mot3(id3, 1); //20


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
void moveAbsolute(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6);
void moveIncremental(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6);

// Arduino functions
void setup() {
  Serial.begin(9600); // set the baud rate, must be the same for both machines
  while (!Serial);
  mot1.init();
  mot2.init();
  mot3.init();
  dataPack outgoingMessage{(int32_t)(mot1.getPosition()), (int32_t)(mot2.getPosition()), (int32_t)(mot3.getPosition()), 0, 0, 0};
  sendMessage(outgoingMessage);
  //pinMode(test.getProximitySensorPin(1), INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  //pinMode(test.getProximitySensorPin(2), INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  //pinMode(test.getMotorPin(1),OUTPUT);
  //pinMode(test.getMotorPin(2),OUTPUT);
  //pinMode(test.getDrivePin(),OUTPUT);
}
long oldPosition  = -999; //variable de départ pour l'encodeur
void loop() {
  /* long newPosition = myEnc.read();
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    Serial.println(newPosition);
  }
  test.setEnableDrive(true);
  test.setMotorState(-1);
  test.runAxialCalibration();
  Serial.println("done");
  while (1)*/

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

      if(data.mode == 'a')
      {
        moveAbsolute(data.p1, data.p2, data.p3, data.p4, data.p5, data.p6);
      }
      else if(data.mode == 'i')
      {
        moveIncremental(data.p1, data.p2, data.p3, data.p4, data.p5, data.p6);
      }
      else if(data.mode == 's')
      {
        // Do nothing apart from sending message
      }
      else if(data.mode == 'c')
      {
        //TODO: connect to calibration function
      }



      dataPack outgoingMessage{(byte)'a', (int32_t)(mot1.getPosition()), (int32_t)(mot2.getPosition()), (int32_t)(mot3.getPosition()), 0, 0, 0, (byte)'\0'};
      sendMessage(outgoingMessage);
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
    mot1.moveMotor(p1);
    mot2.moveMotor(p2);
    mot3.moveMotor(p3);
}

/** \brief move motors to an incremental position
    \param p1, ..., p6 : position for each motor
*/
void moveIncremental(uint16_t p1, uint16_t p2, uint16_t p3, uint16_t p4, uint16_t p5, uint16_t p6)
{
  //TODO
}
