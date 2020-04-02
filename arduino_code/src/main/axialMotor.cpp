#include <Arduino.h>
#include "axialMotor.h"
#include "encoder/Encoder.cpp"

/** \brief Construct the axial motor with initial states/pinout
  * \param motorInitialState : Motor start state (0,1,-1). 0 means going CCW, 1 CW and -1 STOP.
  * \param ProxSensor1Value : Pin value of the first proximity sensor
  * \param ProxSensor2Value : Pin value of the second proximity sensor
  */
axialMotor::axialMotor(int enAPinValue, int motorInitialState,int pinCWOutputValue, int pinCCWOutputValue, int proxSensor1Value,int proxSensor2Value,int pinEncoderL,int pinEncoderR)
{
  motorState = motorInitialState;
  enAPin = enAPinValue;
  pinCWOutput = pinCWOutputValue;
  pinCCWOutput = pinCCWOutputValue;  
  proximitySensor1Pin = proxSensor1Value;
  proximitySensor2Pin = proxSensor2Value;
  enc = new Encoder(pinEncoderL,pinEncoderR);
  homePosition = 0;
  oldPosition = -999;
  calibrationCase = -1;
  totalClicksOnRobot = 1000; //This value needs to be chanded by the one measured at client
  totalIncrementOfSlider = 4095;

}

/** \brief Construct the axial motor with no initial states/pinout. Motor state is then set to STOP (-1), and proximity sensor pinout to 51 and 53 by default.
  */
axialMotor::axialMotor()
{
  motorState = -1;
  enAPin = 53;
  pinCWOutput = A1;
  pinCCWOutput = A2;  
  proximitySensor1Pin = 19;
  proximitySensor2Pin = 20;
  enc = new Encoder(2,3);
  homePosition = 0;
  oldPosition = -999;
  calibrationCase = -1;
  totalClicksOnRobot = 1000; //This value needs to be chanded by the one measured at client
  totalIncrementOfSlider = 4095;
}

axialMotor::~axialMotor()
{
  delete enc;
}

/** \brief Checks if the requirement to make the motor stop are met. 
 *  /return bool : value confirming if the motor should slow down or not.
 */
bool axialMotor::shouldSlowDown(bool slowItTOP,bool slowItBOT)
{
  if (slowItTOP == true)
  {
    if ( motorState == 1 )
    {
      //Serial.println("Sortie 1");
      return true;
    }
    else if (motorState == 0  || motorState == -1)
    {
      //Serial.println("Sortie 2");
      return false;
    }
    
    else
    {
      //Serial.println("Sortie 3");
      return false;
    }
  }

  else if (slowItBOT == true)
  {
    if (motorState == 1  || motorState == -1)
    {
     // Serial.println("Sortie 4");
      return false;
    }
  
    else if (motorState == 0)
    {
      //Serial.println("Sortie 5");
      return true;
    }
    
    else
    {
     // Serial.println("Sortie 6");
      return false;
    }
  }
}

/** \brief Calibrate the assembly's vertical axis using the upper proximity sensor.
  * \param motorInitialState : Motor start state (0,1,-1). 0 means going CCW, 1 CW and -1 STOP.
  * \param ProxSensor1Value : Pin value of the first proximity sensor.
  * \param ProxSensor2Value : Pin value of the second proximity sensor.
  * \return bool : Boolean value verifying the end of the calibration sequence.
  */
int axialMotor::runAxialCalibration(int newCase,int newHomePosition)
{
    if (newCase == 0)
    {
      setMotorState(1);
      return 1;
    }
      
    else if (newCase == 1)
    {  
      setMotorState(-1);
      homePosition = newHomePosition;
      return -1; 
    }
    
    else
    {
      return -2;
    }
}

/** \brief Sets the motor state value to a given value of 0,1 or -1. If the value is not in this range, the function forces -1. It then changes the pin output to the motor accordingly
 *  \param StateValue : value confirming if the motor should slow down or not.
 */
void axialMotor::setMotorState(int stateValue)
{
//Serial.println("JE PASSE POUR CHANGER LE MOTEUR");
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
       analogWrite(getMotorPin(2),255);
       analogWrite(getMotorPin(1),0);
     }
     
  else if (motorState == 0)
     {
      // Serial.println("ICI SI LE STATE VALUE EST DE 0");
       analogWrite(getMotorPin(2),0);
       analogWrite(getMotorPin(1),255);

     }
     
  else if (motorState == -1)
     {
      // Serial.print("ICI SI LE STATE VALUE EST DE -1");
       analogWrite(getMotorPin(2),1); //si erreur, mettre les deux à zéro
       analogWrite(getMotorPin(1),1);
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
int axialMotor::getProximitySensorPin(int sensorNumber)
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
int axialMotor::getProximitySensorValue(int sensorNumber)
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

/** \brief Enables of disables the drive pin on the L298N DC drive  
 *  \param driveValue : bool value corresponding to the "ON" or "OFF" behaviour of the drive
 */
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

void  axialMotor::runIt(long encPosition,bool* slowItTOP, bool* slowItBOT,int requiredPosition)
{

  if (encPosition != oldPosition) 
  {
    //Serial.println(encPosition);
    oldPosition = encPosition;
  }

  if (calibrationCase == 0)
  {
    Serial.println("Calibration case = 0");
    modifyCalibrationCase(runAxialCalibration(calibrationCase,encPosition));
    Serial.println(calibrationCase);
  }
  if (calibrationCase == 1 && *slowItTOP == true)
  {
    Serial.println("Calibration case = 1");
    modifyCalibrationCase(runAxialCalibration(calibrationCase,encPosition));
  }

  if (getProximitySensorValue(1) == 1)
  {
    //Serial.println("slowItTOP = FALSE");
    *slowItTOP = false;
  }
  
  if (getProximitySensorValue(2) == 1)
  {
    //Serial.println("slowItBOT = FALSE");
    *slowItBOT = false;
  }
  
  if (calibrationCase == -1)
  {
    Serial.println("hi");
    goToPosition(encPosition,requiredPosition);
  }

}

/** \brief Gives the status of the drive pin on the L298N DC drive. 
 *  \return int : actual state of the drive.
 */
int axialMotor::getDriveState()
{
  return digitalRead(enAPin);
}

/** \brief Gives the arduino pin of the L298N drive pin . 
 *  \return int : pin where the drive is connected to.
 */
int axialMotor::getDrivePin()
{
  return enAPin;
}

/** \brief Bring the robot go to a specific position. It computes the clicks needed, compares it to the actual clicks and moves the robot accordingly. 
 *  \param percentageOfTravel : int value corresponding to the percentage (ex: 10, 25, etc.) of the rail you want to be on.
 *  \return bool : Returns true.
 */
bool axialMotor::goToPosition(int encPosition,int requiredPosition)
{
  int positionInClicks = positionToClicks(requiredPosition);
  int tolerance = abs(encPosition - positionInClicks);
  if (tolerance > 4)
  {
    
    if (encPosition - positionInClicks > 0)
    {
      setMotorState(1);
      return true;
    }
    
    else if (encPosition - positionInClicks < 0)
    {
      setMotorState(0);
      return true;
    }
  }
 else
 {
    setMotorState(-1);
    return true;
 }
}

/** \brief Gives the position in clicks from the percentage of travel required by the user.
 *  \param percentageOfTravel : int value corresponding to the percentage (ex: 10, 25, etc.) of the rail you want to be on.
 *  \return int : Value in clicks of the input in percentage.
 */
int axialMotor::positionToClicks(int requiredPosition)
{

  double percent = double(requiredPosition)/totalIncrementOfSlider;
  return homePosition - (percent * totalClicksOnRobot) ;
}

void  axialMotor::modifyCalibrationCase(int newCaseValue)
{
    calibrationCase = newCaseValue;  
}

long  axialMotor::getCalibrationCase()
{
  return calibrationCase;
}
