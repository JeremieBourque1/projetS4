
class axialMotor
{
  public:
  axialMotor(int enAPin, int motorInitialState,int pinCWOutputValue, int pinCCWOutputValue, int ProxSensor1Value,int ProxSensor2Value);
  axialMotor();
  bool shouldSlowDown();
  bool runAxialCalibration();
  void setMotorState(int stateValue);
  void setEnableDrive(bool driveValue);
  int getMotorState();
  int getDriveState();
  int getProximitySensorPin(bool sensorNumber);
  int getProximitySensorValue(bool sensorNumber);
  int getMotorPin(int directionNumber);
  int getDrivePin();
  
  private:
  int motorState;
  int enAPin; //digital pin for enabling the motor control
  int pinCWOutput; //Pin for CW control (#1)
  int pinCCWOutput; //Pin for CCW control (#2)
  int proximitySensor1Pin; //Connected pin for sensor #1
  int proximitySensor2Pin; //Connected pin for sensor #2s
};

/** \brief Construct the axial motor with initial states/pinout
  * \param motorInitialState : Motor start state (0,1,-1). 0 means going CCW, 1 CW and -1 STOP.
  * \param ProxSensor1Value : Pin value of the first proximity sensor
  * \param ProxSensor2Value : Pin value of the second proximity sensor
  */
axialMotor::axialMotor(int enAPinValue, int motorInitialState,int pinCWOutputValue, int pinCCWOutputValue, int ProxSensor1Value,int ProxSensor2Value)
{
  motorState = motorInitialState;
  //setMotorState(motorState);
  enAPin = enAPinValue;
  pinCWOutput = pinCWOutputValue;
  pinCCWOutput = pinCCWOutputValue;  
  proximitySensor1Pin = ProxSensor1Value;
  proximitySensor2Pin = ProxSensor2Value;

}

/** \brief Construct the axial motor with no initial states/pinout. Motor state is then set to STOP (-1), and proximity sensor pinout to 51 and 53 by default.
  */
axialMotor::axialMotor()
{
  motorState = -1;
  //setMotorState(motorState);
  enAPin = 45;
  pinCWOutput = 47;
  pinCCWOutput = 49;  
  proximitySensor1Pin = 51;
  proximitySensor2Pin = 53;
}

/** \brief Checks if the requirement to make the motor stop are met. 
 *  /return bool : value confirming if the motor should slow down or not.
 */
bool axialMotor::shouldSlowDown()
{
 int proximitySensor1Reading = digitalRead(getProximitySensorPin(1)); //defines the input to pins #51. The input is HIGH when nothing is capted this is the top sensor
  //Serial.print("la valeur de proximite est de :");
  //Serial.print(proximitySensor1Reading);
  if (proximitySensor1Reading == false && getMotorState() == true || getMotorState() == -1)
  {
   // Serial.print("Je lis le capteur et le moteur monte");
    return true;
  }

  else if (proximitySensor1Reading == false && getMotorState() == false)
  {
    //Serial.print("Je lis le capteur et le moteur DESCEND");
    return false;
  }
  else
  {
    return false;
  }
 int proximitySensor2Reading = digitalRead(getProximitySensorPin(2)); //defines the input to pin #53. The input is HIGH when nothing is capted
 //Serial.print("TU ENTRE EN CAPTEUR 2!");

  if (proximitySensor2Reading == false && getMotorState() == true)
  {
  //  Serial.print("CAPTEUR 2 UNDER CONSTRUCTION");
    return false;
  }

  else if (proximitySensor2Reading == false && getMotorState() == false || getMotorState() == -1)
  {
   // Serial.print("CAPTEUR 2 UNDER CONSTRUCTION");
    return true;
  }
  
  else
  {
    return false;
  }
}

/** \brief Calibrate the assembly's vertical axis using the upper proximity sensor.
  * \param motorInitialState : Motor start state (0,1,-1). 0 means going CCW, 1 CW and -1 STOP.
  * \param ProxSensor1Value : Pin value of the first proximity sensor.
  * \param ProxSensor2Value : Pin value of the second proximity sensor.
  * \return bool : Boolean value verifying the end of the calibration sequence.
  */
bool axialMotor::runAxialCalibration()
{
    setMotorState(1);
    //Serial.print("le moteur tourne maintenant");
    while (shouldSlowDown() == false)
    {
       if (shouldSlowDown() == true)
        {
           setMotorState(-1);
           return true; 
        }
    }
  return false;

}

/** \brief Sets the motor state value to a given value of 0,1 or -1. If the value is not in this range, the function forces -1. It then changes the pin output to the motor accordingly
 *  \param StateValue : value confirming if the motor should slow down or not.
 */
void axialMotor::setMotorState(int stateValue)
{
  //Serial.println("JE PASSE ICI");
    //Serial.println(stateValue);

  if (stateValue != -1 && stateValue != 1 && stateValue != 0)
     {
        //Serial.println("MAUVAISE ENTRÉE, MAINTENANT MOTORSTATE SERA DE :");
        
        stateValue = -1; //doesn't move the motor
     }
  //Serial.println("STATE VALUE correct");
  motorState = stateValue; //Sets the motor value to the new direction value.
   
  if (motorState == 1) //Changes the motor rotation by changing output pin value.
     {
       //Serial.println("ICI SI LE STATE VALUE EST DE 1");
       
       digitalWrite(getMotorPin(1),HIGH);
       digitalWrite(getMotorPin(2),LOW);
       //Serial.print(digitalRead(getMotorPin(1)));
       //Serial.print(digitalRead(getMotorPin(2)));
     }
     
  else if (motorState == 0)
     {
      // Serial.println("ICI SI LE STATE VALUE EST DE 0");
       digitalWrite(getMotorPin(2),HIGH);
       digitalWrite(getMotorPin(1),LOW);
     }
     
  else if (motorState == -1)
     {
      // Serial.print("ICI SI LE STATE VALUE EST DE -1");
       digitalWrite(getMotorPin(2),LOW);
       digitalWrite(getMotorPin(1),LOW);
     }
}

/** \brief gets the motor current state. 
 *  \return int : current state value of the motor.
 */
int axialMotor::getMotorState()
{
  return motorState;
}

/** \brief Gives the proximity sensor pin number on the arduino. 
 *  \param sensorNumber : Boolean value corresponding to the sensor number in the assembly. 1 is the top sensor, 2, the bottom sensor.
 *  \return int : Returns the pin number.
 */
int axialMotor::getProximitySensorPin(bool sensorNumber)
{
  if (sensorNumber == 1)
  {
    return proximitySensor1Pin;
  }
  
  else if (sensorNumber == 2)
  {
    return proximitySensor2Pin;
  }
}

/** \brief Gives a sensor value. All proximity sensors are pulled up.  
 *  \param sensorNumber : Boolean value corresponding to the sensor number in the assembly. 1 is the top sensor, 2, the bottom sensor.
 *  \return int : actual value given off by the sensor.
 */
int axialMotor::getProximitySensorValue(bool sensorNumber)
{
  if (sensorNumber == 1)
  {
    return digitalRead(proximitySensor1Pin);
  }
  
  else if (sensorNumber == 2)
  {
    return digitalRead(proximitySensor2Pin);
  }
}

/** \brief Gives the chosen motor direction pin.  
 *  \param directionNumber : int value corresponding to the direction of the motor in the assembly. 1 is the clockwise direction, 2, the counterclockwise direction.
 *  \return int : actual value of the pin.
 */
int axialMotor::getMotorPin(int directionNumber)
{
  if (directionNumber == 1)
  {
    return pinCWOutput;
  }
  else if (directionNumber == 2)
  {
    return pinCCWOutput;
  }

  else
  {
    return -1;
  }
}

void axialMotor::setEnableDrive(bool driveValue)
{
  if (driveValue == true)
  {
    digitalWrite(enAPin,HIGH);
  }
  else if (driveValue== false)
  {
    digitalWrite(enAPin,LOW);
  }
  else
  {
    digitalWrite(enAPin,LOW);
  }
}

int axialMotor::getDriveState()
{
  return digitalRead(enAPin);
}

int axialMotor::getDrivePin()
{
  return enAPin;
}
