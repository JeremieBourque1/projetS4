#include <Arduino.h>

// Declare constants
const int MESSAGE_SIZE = 12;

// Struct of the data received and sent
struct dataPack {
  int16_t p1;  // Motor 1 position
  int16_t p2;  // Motor 2 position
  int16_t p3;  // Motor 3 position
  int16_t p4;  // Motor 4 position
  int16_t p5;  // Motor 5 position 
  int16_t p6;  // Motor 6 position 
};

// Function prototypes
void readDataToStruct(dataPack *data);
void readMessage(char *message);

// Arduino functions
void setup() {
  Serial.begin(9600); // set the baud rate, must be the same for both machines
  Serial.println("Ready");
}

void loop() {
  if(Serial.available() >= MESSAGE_SIZE) // Only parse message when the full message has been received.
  {
    // Read data
    dataPack data;    
    readDataToStruct(&data);

    // Debug
    Serial.println(data.p1);
    Serial.println(data.p2);
    Serial.println(data.p3);
    Serial.println(data.p4);
    Serial.println(data.p5);
    Serial.println(data.p6);
  }

  // TODO: Call move motor functinons
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
void readDataToStruct(dataPack *data)
//TODO: There should be an end of message byte to avoid confusing two messages
{
  int i = 0;
  byte buf[MESSAGE_SIZE];
  while(Serial.available() && i < MESSAGE_SIZE)
  {
    buf[i] = Serial.read();
    i++;
  }
  memcpy(data, buf, sizeof(*data));
}


