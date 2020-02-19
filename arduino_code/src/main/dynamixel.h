#include <DynamixelWorkbench.h>

// OpenCR device definition
#if defined(__OPENCM904__)
  #define DEVICE_NAME "3" //Dynamixel on Serial3(USART3)  <-OpenCM 485EXP
#elif defined(__OPENCR__)
  #define DEVICE_NAME ""
#endif 

DynamixelWorkbench dxl_wb;
const int BAUDRATE = 57600;

// Initialize Dynamixel servo motor and verify that it is reachable
bool initDynamixel(uint8_t id)
{
  const char *log;
  bool result = false;

  uint16_t model_number = 0;

  bool initSuccess = false;
  bool pingSuccess = false; 

  result = dxl_wb.init(DEVICE_NAME, BAUDRATE, &log);
  if (result == false)
  {
    //Serial.println(log);
    //Serial.println("Failed to init");
  }
  else
  {
    //Serial.print("Succeeded to init : ");
    //Serial.println(BAUDRATE);
    initSuccess = true;  
  }

  result = dxl_wb.ping(id, &model_number, &log);
  if (result == false)
  {
    //Serial.println(log);
    //Serial.println("Failed to ping");
  }
  else
  {
    //Serial.println("Succeeded to ping");
    //Serial.print("id : ");
    //Serial.print(id);
    //Serial.print(" model_number : ");
    //Serial.println(model_number);
    pingSuccess = true;
  }
  if(initSuccess && pingSuccess)
  {
    //Serial.print("Motor id: ");
    //Serial.print(id);
    //Serial.println(" has been initialized successfully") ;
    return true;
  }
  return false;
}


bool setJointMode(uint8_t id)
{
  const char *log;
  bool result = false;
  result = dxl_wb.jointMode(id, 0, 0, &log);
  if (result == false)
  {
    //Serial.println(log);
    //Serial.println("Failed to change joint mode");
    return false;
  }
  else
  {
    //Serial.println("Succeed to change joint mode");
    return true;
  }
}

void moveMotor(uint8_t id, int32_t pos)
{
  dxl_wb.goalPosition(id, pos);
  //Serial.println("Dynamixel is moving...");
}
