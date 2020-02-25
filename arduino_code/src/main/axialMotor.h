
class axialMotor
{
  public:
  axialMotor(int motorInitialState, int ProxSensor1Value,int ProxSensor2Value);
  axialMotor();
  bool shouldSlowDown();
  bool runAxialCalibration();
  void setMotorState(int stateValue);
  int getMotorState();
  int getProximitySensorPin(bool sensorNumber);
  int getProximitySensorValue(bool sensorNumber);

  private:
  int motorState;
  int proximitySensor1Pin; //Connected pin for sensor #1
  int proximitySensor2Pin; //Connected pin for sensor #2s
};

/** \brief Construct the axial motor with initial states/pinout
  * \param motorInitialState : Motor start state (0,1,-1). 0 means going CCW, 1 CW and -1 STOP.
  * \param ProxSensor1Value : Pin value of the first proximity sensor
  * \param ProxSensor2Value : Pin value of the second proximity sensor
  */
axialMotor::axialMotor(int motorInitialState, int ProxSensor1Value,int ProxSensor2Value)
{
  motorState = motorInitialState;
  proximitySensor1Pin = ProxSensor1Value;
  proximitySensor2Pin = ProxSensor2Value;
}

/** \brief Construct the axial motor with no initial states/pinout. Motor state is then set to STOP, and proximity sensor pinout to 51 and 53 by default.
  */
axialMotor::axialMotor()
{
  motorState = -1;
  proximitySensor1Pin = 51;
  proximitySensor2Pin = 53;
}

/** \brief Checks if the requirement to make the motor stop are met. 
 *  /return bool : value confirming if the motor should slow down or not.
 */
bool axialMotor::shouldSlowDown()
{
 int proximitySensor1Reading = digitalRead(getProximitySensorPin(1)); //defines the input to pins #51. The input is HIGH when nothing is capted

  if (proximitySensor1Reading == false && getMotorState() == true || getMotorState() == -1)
  {
    return true;
  }

  if (proximitySensor1Reading == false && getMotorState() == false)
  {
    return false;
  }

 int proximitySensor2Reading = digitalRead(getProximitySensorPin(2)); //defines the input to pin #53. The input is HIGH when nothing is capted

  if (proximitySensor2Reading == false && getMotorState() == true)
  {
    return false;
  }

  if (proximitySensor2Reading == false && getMotorState() == false || getMotorState() == -1)
  {
    return true;
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
    if (shouldSlowDown() == true)
    {
      setMotorState(-1);
      return true; 
    }

    else
    {
        return false;
    }

}

/** \brief Sets the motor state value to a given value of 0,1 or -1. If the value is not in this range, the function forces -1. 
 *  \param StateValue : value confirming if the motor should slow down or not.
 */
void axialMotor::setMotorState(int stateValue)
{
  if (stateValue != -1 || stateValue != 1 || stateValue != 0)
  {
    motorState = -1; //doesn't move the motor
  }
   motorState = stateValue; //Sets the motor value to the new direction value.
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
  
  if (sensorNumber == 2)
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
  
  if (sensorNumber == 2)
  {
    return digitalRead(proximitySensor2Pin);
  }
}
