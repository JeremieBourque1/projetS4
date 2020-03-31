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
void trigShouldSlowDownPin1();
void trigShouldSlowDownPin2();

//axialMotor axialMotor(13,-1,A1,A2,51,53,2,3);
axialMotor test; //classe test
//Encoder myEnc(2, 3); //classe de lecture de l'encodeur

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
  attachInterrupt(digitalPinToInterrupt(test.getProximitySensorPin(1)), trigShouldSlowDownPin1, FALLING);
  attachInterrupt(digitalPinToInterrupt(test.getProximitySensorPin(2)), trigShouldSlowDownPin2, FALLING);
  pinMode(test.getMotorPin(1),OUTPUT);
  pinMode(test.getMotorPin(2),OUTPUT);
  pinMode(test.getDrivePin(),OUTPUT);

  pinMode(38,OUTPUT); //power for the drive
  digitalWrite(38,HIGH); //power for the drive
}
int oldPosition=-999;
int calibrationCase = -1;
bool slowItTOP = false;
bool slowItBOT = false;

void loop() {
  
long encPosition = test.enc->read();

  if (encPosition != oldPosition) 
  {
    Serial.println(encPosition);
    oldPosition = encPosition;
  }

  test.setEnableDrive(true);
  test.setMotorState(1);

  if (calibrationCase == 0)
  {
      Serial.println("Calibration case = 0");
    calibrationCase = test.runAxialCalibration(calibrationCase,encPosition);
    Serial.println("ÉTAPE 1");
    Serial.println(calibrationCase);
  }
  if (calibrationCase == 1 && slowItTOP == true)
  {
    Serial.println("Calibration case = 1");
    calibrationCase = test.runAxialCalibration(calibrationCase,encPosition);
    Serial.println(calibrationCase);
  }

  if (test.getProximitySensorValue(1) == 0)
  {
   // Serial.println(test.getProximitySensorValue(test.getProximitySensorPin(1)));
    //Serial.println("le sensor du TOP est actif!");
    slowItTOP = false;
  }
  
  if (test.getProximitySensorValue(2) == 0)
  {
    //Serial.println(test.getProximitySensorValue(2);
    //Serial.println("le sensor du bas est actif!");
    slowItBOT = false;
  }
 /* if (test.shouldSlowDown(test.getProximitySensorPin(1)) == true || test.shouldSlowDown(test.getProximitySensorPin(2)) == true)
  {
    //Serial.println("J'arrete le moteur car je m'y en approche dangereusement");
    test.setMotorState(-1);
  }*/
 
   //Serial.println(test.getProximitySensorValue(1));
  // Serial.println(test.getProximitySensorValue(2));
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

void trigShouldSlowDownPin1()
{
    Serial.println("ICITTE1");
    slowItTOP = true;

}

void trigShouldSlowDownPin2()
{
    Serial.println("ICITTE2");
    slowItBOT = true;

}
