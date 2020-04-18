#include <Arduino.h>
#include "axialMotor.h"
// We used those links to modify encoder.cpp
//https://github.com/ROBOTIS-GIT/OpenCM9.04/pull/30/files
//http://emanual.robotis.com/docs/en/parts/controller/opencr10/#layoutpin-map
#include "encoder/Encoder.cpp"

/** \brief Construct the axial motor with initial states/pinout
  * \param enAPinValue : Int value corresponding to the value of the activation pin of the DC drive.
  * \param motorInitialState : Motor start state (0,1,-1). 0 means going CCW, 1 CW and -1 STOP.
  * \param pinCWOutputValue : Int value of the clockwise pin of the drive.
  * \param pinCCWOutputValue : Int value of the counter clockwise pin of the drive.
  * \param ProxSensor1Value : Int value of the pin of the first proximity sensor.
  * \param ProxSensor2Value : Int value of the pin of the second proximity sensor.
  * \param pinEncoderL : Int value of the pin of the Left encoder.
  * \param pinEncoderR : Int value of the pin of the Right encoder.
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
  totalClicksOnRobot = 5000; //This value needs to be chanded by the one measured at client
  totalIncrementOfSlider = 4095;

}

/** \brief Construct the axial motor with no initial states/pinout. See constructor with arguments for explanations of variables.
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
  totalClicksOnRobot = 5000; //This value needs to be chanded by the one measured at client
  totalIncrementOfSlider = 4095;
}

axialMotor::~axialMotor()
{
  delete enc;
}

/** \brief Checks if the requirement to make the motor stop are met. 
 *  \param slowItTOP : Value of the boolean triggered by the interrupt of the top proximity sensor.
 *  \param slowItBOT : Value of the boolean triggered by the interrupt of the bottom proximity sensor.
 *  /return bool : value confirming (true) if the motor should slow down or not (false).
 */
bool axialMotor::shouldSlowDown(bool slowItTOP,bool slowItBOT)
{
  if (slowItTOP == true)
  {
    if ( motorState == 1 )
    {
      return true;
    }
    else if (motorState == 0  || motorState == -1)
    {
      return false;
    }
    
    else
    {
      return false;
    }
  }

  else if (slowItBOT == true)
  {
    if (motorState == 1  || motorState == -1)
    {
      return false;
    }
  
    else if (motorState == 0)
    {
      return true;
    }
    
    else
    {
      return false;
    }
  }
}

/** \brief Calibrate the assembly's vertical axis using the top proximity sensor.
  * \param newCase : Int value of the case for the calibration. Case 0 is the first enter in the function (first step). Case 1 is the second step and -1 is the initialize.
  * \param newHomePosition : Int value of the encoder given to update the homePosition variable.
  * \return int : Returns the value of the next case to be executed. Example, if case 0 is run, the return will be 1. If the case 1 is run ,the return will be -1;
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
      //Serial.print("This is home: ");
      //Serial.println(homePosition);
      return -1; 
    }
    
    else
    {
      return -2;
    }
}

/** \brief Sets the motorState variable value to a given value of 0,1 or -1. If the value is not in this range, the function forces -1. It then changes the pin output to the motor accordingly. 1,0 and -1 are respectively CW,CCW and stop.
 *  \param StateValue : value sent to make the motor move.
 */
void axialMotor::setMotorState(int stateValue)
{
//Serial.println("JE PASSE POUR CHANGER LE MOTEUR");
    //Serial.println(stateValue);

  if (stateValue != -1 && stateValue != 1 && stateValue != 0)
     {
        //Serial.println("Setting motor to: -1");
        stateValue = -1; //doesn't move the motor
     }
     
  //Serial.println("STATE VALUE correct");
  motorState = stateValue; //Sets the motor value to the new direction value.
   
  if (motorState == 1) //Changes the motor rotation by changing output pin value.
     {
       //Serial.println("Setting motor to: 1");
       analogWrite(pinCCWOutput,255);
       analogWrite(pinCWOutput,0);
     }
     
  else if (motorState == 0)
     {
       //Serial.println("Setting motor to: 0");
       analogWrite(pinCCWOutput,0);
       analogWrite(pinCWOutput,255);

     }
     
  else if (motorState == -1)
     {
       //Serial.println("Setting motor to: -1 (2)");
       analogWrite(pinCCWOutput,1); //si erreur, mettre les deux à zéro
       analogWrite(pinCWOutput,1);
     }
}

/** \brief gets the motor current state. 
 *  \return int : Current state value of the motor.
 */
int axialMotor::getMotorState()
{
  return motorState;
}

/** \brief Gives the proximity sensor pin number on the arduino. 
 *  \param sensorNumber : int value corresponding to the sensor number in the assembly. 1 is the top sensor, 2, the bottom sensor.
 *  \return int : Returns the pin number of the chose sensor.
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
 *  \param sensorNumber : Int value corresponding to the sensor number in the assembly. 1 is the top sensor, 2, the bottom sensor.
 *  \return int : actual value given off by the chosen sensor.
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
 *  \param directionNumber : Int value corresponding to the direction of the motor in the assembly. 1 is the clockwise direction, 2, the counterclockwise direction.
 *  \return int : actual value of the chosen pin. If values given to the function are not right, the function will return -1.
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
 *  \param driveValue : Bool value corresponding to the "ON" (true) or "OFF" (false) behaviour of the drive
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

/** \brief This function makes the whole vertical axis function. It checks for calibration cases, checks if 
 *  interrupts have been trigged and moves the arm to the desired position. This means that the function utilises runAxialCalibration(),
 *  getProximitySensorValue(),modifyCalibrationCase() and goToPosition().
 *  \param encPosition : Long value used to give the wanted position.
 *  \param slowItTOP : Boolean pointer to the stop value of the top interrupt sequence.
 *  \param slowItBOT : Boolean pointer to the stop value of the bottom interrupt sequence.
 *  \param requiredPosition : Int value representing the wanted position.
 */
void  axialMotor::runIt(long encPosition,bool* slowItTOP, bool* slowItBOT,int requiredPosition, bool* buttonCalibration)
{
  if (encPosition != oldPosition) 
  {
    //Serial.println(encPosition);
    oldPosition = encPosition;
  }
  if (*buttonCalibration == true)
  {
    calibrationCase = 0;
    *buttonCalibration == false;
  }
  if (calibrationCase == 0)
  {
    //Serial.println("Calibration case = 0");
    calibrationCase = runAxialCalibration(calibrationCase,encPosition);
  }
  if (calibrationCase == 1 && *slowItTOP == true)
  {
    //Serial.println("Calibration case = 1");
    calibrationCase = runAxialCalibration(calibrationCase,encPosition);
  }

  if (digitalRead(proximitySensor1Pin) == 1)
  {
    //Serial.println("slowItTOP = FALSE");
    *slowItTOP = false;
  }
  
  if (digitalRead(proximitySensor2Pin) == 1)
  {
    //Serial.println("slowItBOT = FALSE");
    *slowItBOT = false;
  }
  //Serial.println("runIt checks for position reach once calibration is done");
  if (calibrationCase == -1)
  {
    //Serial.println("calibration is done so runIt calls goToPosition");
    goToPosition(encPosition,requiredPosition);
  }

}

/** \brief Gives the status of the drive pin on the dc drive. 
 *  \return int : actual state of the drive.
 */
int axialMotor::getDriveState()
{
  return digitalRead(enAPin);
}

/** \brief Gives the arduino pin of the drive pin . 
 *  \return int : pin where the drive pin of the dc drive is connected to.
 */
int axialMotor::getDrivePin()
{
  return enAPin;
}

/** \brief Bring the robot go to a specific position. It computes the clicks needed, compares it to the actual clicks and moves the robot accordingly with setMotorState().
 *  \param encPosition : Int value of the actual position of the arm.
 *  \param requiredPosition : Int value of the wanted position of the arm.
 *  \return bool : Returns true when done.
 */
bool axialMotor::goToPosition(int encPosition,int requiredPosition)
{
  int acceptedTol = 25;
  int positionInClicks = positionToClicks(requiredPosition);
  int tolerance = abs(positionInClicks - encPosition);
  //Serial.println(tolerance);
  if (tolerance > acceptedTol) //if tolerance not reached
  {
    //Serial.println(positionInClicks - encPosition);
    if (positionInClicks - encPosition  < 0)
    { 
     /* Serial.print("position actuelle: ");
      Serial.println(encPosition );
      Serial.print("position Requise: ");
      Serial.println(positionInClicks);
      Serial.print("Différence: ");
      Serial.println(encPosition-positionInClicks);*/
      setMotorState(1);
      //Serial.println("MONTE");
      return true;
    }
    
    else if (positionInClicks - encPosition > 0)
    {
      //Serial.println("DESCEND");
      setMotorState(0);
      return true;
    }
  }
 else if (tolerance <= acceptedTol)
 {
  //Serial.println("Second out, tolerance is respected");
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

  double percent = (double)requiredPosition/totalIncrementOfSlider; 
  //Serial.println(percent);
  //Serial.println(homePosition + (percent * totalClicksOnRobot));
  return homePosition + (percent * totalClicksOnRobot) ;
}

/** \brief modify the calibration case.
 *  \param newCaseValue : int value corresponding to the new case to run.
 */
void  axialMotor::modifyCalibrationCase(int newCaseValue)
{
    calibrationCase = newCaseValue;  
}

/** \brief Gives the actual calibration case.
 *  \return long : Value of the calibration case
  */
int  axialMotor::getCalibrationCase()
{
  return calibrationCase;
}
