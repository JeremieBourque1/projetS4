#include "encoder/Encoder.h"

class axialMotor
{
  public:
  axialMotor(int enAPin, int motorInitialState,int pinCWOutputValue, int pinCCWOutputValue, int ProxSensor1Value,int ProxSensor2Value,int pinEncoderL,int pinEncoderR);
  axialMotor();
  ~axialMotor();
  bool shouldSlowDown(bool slowItTOP , bool slowItBOT);
  int runAxialCalibration(int cas,int newHomePosition);
  void setMotorState(int stateValue);
  void setEnableDrive(bool driveValue);
  void runIt(long encPosition,bool* slowItTOP, bool* slowItBOT, int requiredPosition, bool buttonCalibration);
  int getMotorState();
  int getDriveState();
  int getProximitySensorPin(int sensorNumber);
  int getProximitySensorValue(int sensorNumber);
  int getMotorPin(int directionNumber);
  int getDrivePin();
  bool goToPosition(int encPosition,int requiredPosition);
  int positionToClicks(int lengthCm);
  void modifyCalibrationCase(int newCaseValue);
  int getCalibrationCase();
  Encoder* enc;
  
  private:
  int motorState;
  int enAPin; //digital pin for enabling the motor control
  int pinCWOutput; //ANALOG Pin for CW control (#1)
  int pinCCWOutput; //ANALOG Pin for CCW control (#2)
  int proximitySensor1Pin; //Connected pin for sensor #1
  int proximitySensor2Pin; //Connected pin for sensor #2s
  long homePosition; //home position of encoder
  long oldPosition; //starting encoder variable
  long calibrationCase;
  long totalClicksOnRobot;
  int totalIncrementOfSlider;
};
