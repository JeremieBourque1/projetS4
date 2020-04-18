#include "encoder/Encoder.h"

class axialMotor
{
  public:
  axialMotor(int enAPin, int motorInitialState,int pinCWOutputValue, int pinCCWOutputValue, int ProxSensor1Value,int ProxSensor2Value,int pinEncoderL,int pinEncoderR);
  axialMotor();
  ~axialMotor();
  bool shouldSlowDown(bool slowItTOP , bool slowItBOT);
  int runAxialCalibration(int cas);
  void setMotorState(int stateValue);
  void setEnableDrive(bool driveValue);
  void runIt(bool* slowItTOP, bool* slowItBOT, uint16_t requiredPosition, bool* buttonCalibration);
  int getMotorState();
  int getDriveState();
  int getProximitySensorPin(int sensorNumber);
  int getProximitySensorValue(int sensorNumber);
  int getMotorPin(int directionNumber);
  int getDrivePin();
  bool goToPosition(uint16_t requiredPosition);
  int positionToClicks(uint16_t lengthCm);
  void modifyCalibrationCase(int newCaseValue);
  int getCalibrationCase();
  uint16_t getPosition(int calibrationCase);
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
  int calibrationCase; //gives the calibration step for motor calibration
  float totalClicksOnRobot; //Total clicks of the robot's power screw
  float totalIncrementOfSlider; // Number of incremenet of the slider.
  int acceptedTol; //TODO: match tolerance with RPM and increments.
};
