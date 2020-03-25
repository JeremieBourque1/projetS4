#include "encoder/Encoder.h"

class axialMotor
{
  public:
  axialMotor(int enAPin, int motorInitialState,int pinCWOutputValue, int pinCCWOutputValue, int ProxSensor1Value,int ProxSensor2Value,int pinEncoderL,int pinEncoderR);
  axialMotor();
  ~axialMotor();
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
  bool goToPosition(int positionRequired);
  int positionToClicks(int lengthCm);
  Encoder* enc;
  
  private:
  int motorState;
  int enAPin; //digital pin for enabling the motor control
  int pinCWOutput; //ANALOG Pin for CW control (#1)
  int pinCCWOutput; //ANALOG Pin for CCW control (#2)
  int proximitySensor1Pin; //Connected pin for sensor #1
  int proximitySensor2Pin; //Connected pin for sensor #2s
  long homePosition; //starting encoder variable
};
