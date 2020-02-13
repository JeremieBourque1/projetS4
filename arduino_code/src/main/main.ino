#include <Arduino.h>
#include "dynamixel.h" 

// Declare constants
int proximitySensor1 = 2;
int proximitySensor2 = 4;
const int MESSAGE_SIZE = 13;
char endOfMessageChar = '\0';
const int id1 = 221;


// Struct of the data received and sent
struct dataPack {
  uint16_t p1;  // Motor 1 position
  uint16_t p2;  // Motor 2 position
  uint16_t p3;  // Motor 3 position
  uint16_t p4;  // Motor 4 position
  uint16_t p5;  // Motor 5 position 
  uint16_t p6;  // Motor 6 position 
  char end;    // End of message character
};

// Function prototypes
bool readDataToStruct(dataPack *data);
void readMessage(char *message);
bool initDynamixel(uint8_t id);
bool setJointMode(uint8_t id);
void moveMotor(uint8_t id, int32_t pos);
bool shouldSlowDown(bool motorDirection);

// Arduino functions
void setup() {
  Serial.begin(9600); // set the baud rate, must be the same for both machines
  while(!Serial);
  initDynamixel(id1);
  setJointMode(id1);
  Serial.println("Ready");
  pinMode(proximitySensor1, INPUT_PULLUP); //Set input as a pull-up for proximity sensor
  pinMode(proximitySensor2, INPUT_PULLUP); //Set input as a pull-up for proximity sensor
}

void loop() {
  if(Serial.available() >= MESSAGE_SIZE) // Only parse message when the full message has been received.
  {
    // Read data
    dataPack data;    
    if(readDataToStruct(&data))
    {
      // Debug
      Serial.println(data.p1);
      Serial.println(data.p2);
      Serial.println(data.p3);
      Serial.println(data.p4);
      Serial.println(data.p5);
      Serial.println(data.p6);
      //Serial.println(data.end);

      // TODO: Call move motor functinons
      moveMotor(id1, data.p1);
    }
    else
    {
      Serial.println("Failed to parse message");
    }
  }
}

// Functions

// Iterates through message one character at a time until the end character is found and returns a char array of the message.
// param: message: char*
// return: message: char* 
void readMessage(char *message)
{
  int count = 0;
  char c;
    
    do
    {
      if(Serial.available())
      {
        c = Serial.read();
        message[count] = c;
        count++;
      }
    } while(c != '\0');
}


// Iterates through message one byte at a time until no more bytes are availabe of the buffer is full and adds them to the buffer.
// param: buf: byte[]
// return: buf: byte[]
//         bool : success(true), failed(false)
bool readDataToStruct(dataPack *data)
{
  int i = 0;
  byte buf[MESSAGE_SIZE];
  while(Serial.available() && i < MESSAGE_SIZE)
  {
    buf[i] = Serial.read();
    i++;
  }
  memcpy(data, buf, sizeof(*data));
  if(data->end != endOfMessageChar) // if the last character is not the end-of-message character, message is corrupted
    return false;
    
  return true;
}

//Checks the sensor's state and the motor direction. If motor is moving toward sensor and the sensor is FALSE
// , it sends TRUE. If motor is moving away from sensor and sensor is FALSE, it sends FALSE.
bool shouldSlowDown(bool motorDirection)
{
  proximitySensor1 = digitalRead(2); //defines the input to pin #2. The input is HIGH when nothing is capted

  if (proximitySensor1 == false && motorDirection == true)
  {
    return true;
  }

  if (proximitySensor1 == false && motorDirection == false)
  {
    return false;
  }
  proximitySensor2 = digitalRead(4); //defines the input to pin #4. The input is HIGH when nothing is capted

  if (proximitySensor2 == false && motorDirection == true)
  {
    return false;
  }

  if (proximitySensor2 == false && motorDirection == false)
  {
    return true;
  }
  
}
