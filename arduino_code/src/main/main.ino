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
void sendMessage(dataPack message);
bool initDynamixel(uint8_t id);
bool setJointMode(uint8_t id);
void moveMotor(uint8_t id, int32_t pos);
bool shouldSlowDown(int motorDirection);
bool runAxialCalibration(int motorDirection,int* motor);
bool setAxialMotorDirection(int directionValue, int* motor);
bool checkAxialMotorDirection(int directionValue, int* motor);

// Arduino functions
void setup() {
  Serial.begin(9600); // set the baud rate, must be the same for both machines
  while(!Serial);
  initDynamixel(id1);
  setJointMode(id1);
  //Serial.println("Ready");
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
      //Serial.println(data.p1);
      //Serial.println(data.p2);
      //Serial.println(data.p3);
      //Serial.println(data.p4);
      //Serial.println(data.p5);
      //Serial.println(data.p6);
      //Serial.println(data.end);
      //byte* serializedMessage = (byte*)&data, sizeof(data);
      //Serial.println(serializedMessage);
      void sendMessage(dataPack data);

      // TODO: Call move motor functinons
      moveMotor(id1, data.p1);
    }
    else
    {
      //Serial.println("Failed to parse message");
    }
  }
}

// Functions

/** \brief Iterates through message one character at a time until the end character is found and returns a char array of the message.
  * \param message : empty character array
  * \return message : character array containing message 
  */
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


/** \brief Iterates through message one byte at a time casts it to a dataPack struct.
  * \param data : empty dataPack object the message will be written to
  * \return data : dataPack object containging the unpacked message data
  */
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


/** \brief Sends an encoded message over serial
  * \param message : empty dataPack object the message will be written to
  */
void sendMessage(dataPack message)
{
  Serial.write((byte*)&message, sizeof(message));
}


/** \brief Checks to see if the vertical axis motor should slow down
  * \param motorDirection : integer indicating the direction of the motor 1 = UP, 0 = DOWN
  * \return bool indicating if the motor should slow down
  * 
  * If motor is moving toward sensor and the sensor is FALSE, it returns TRUE.
  * If motor is moving away from sensor and sensor is FALSE, it returns FALSE.
  */
bool shouldSlowDown(int motorDirection)
{
  proximitySensor1 = digitalRead(2); //defines the input to pin #2. The input is HIGH when nothing is capted

  if (proximitySensor1 == false && motorDirection == true || motorDirection == -1)
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

  if (proximitySensor2 == false && motorDirection == false || motorDirection == -1)
  {
    return true;
  }

}


/** \brief Executes the calibration of the vertical axis
  * \param motorDirection : direction in which the calibration will be run
  * \param motor : motor id
  * \return bool
  * 
  * goes towards a limit switch to set a travel limit. Returns TRUE if limit is reached, FALSE if error occurs.
  * motorDirection Takes values of (-1 false true). -1 stands for STOP, false to go down, true for going up.
  * This function takes a motor direction and a pointer to the axial motor.
  */
bool runAxialCalibration(int motorDirection,int* motor)
{
    if (shouldSlowDown(motorDirection) == true) //    //TODO: Add a setSpeed() function?
    {
        if (setAxialMotorDirection(-1, motor) == true)
        {
            return true; //
        }
    }

    else
    {
        return false;
    }

}


/** \brief Executes the calibration of the vertical axis
  * \param directionValue : integer representing the direction of the motor
  * \param motor : motor id
  * \return bool
  * 
  * Set the axial motor direction to an int value between -1 false and true.-1 stands for STOP, false to go down, true for going up.
  * The function also calls checkAxialMotorDirection() to ensure the motor is at the right direction.
  */
bool setAxialMotorDirection(int directionValue, int* motor)
{
    *motor = directionValue; //Sets the motor value to the new direction value.
    if (checkAxialMotorDirection(directionValue, motor) == true ); //if the value is verified to be correct, the function gives true.checkAxialMotorDirection
    {
        return true;
    }

    if (checkAxialMotorDirection(directionValue, motor) == false );
    {
        return false;
    }
}



/** \brief Checks if the motor value is correctly set to the required value.
  * \param directionValue : integer representing the direction of the motor
  * \param motor : motor id
  * \return bool
  */
bool checkAxialMotorDirection(int directionValue, int* motor)
{
    if (*motor == directionValue)
    {
        return true;
    }
    else
    {
        return false;
    }
}
