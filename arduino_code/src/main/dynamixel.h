#include <DynamixelWorkbench.h>

// OpenCR device definition
#if defined(__OPENCM904__)
  #define DEVICE_NAME "3" //Dynamixel on Serial3(USART3)  <-OpenCM 485EXP
#elif defined(__OPENCR__)
  #define DEVICE_NAME ""
#endif 

class Dynamixel {
  private:
    DynamixelWorkbench dxl_wb;
    const int BAUDRATE = 57600;
    //! Dynamixel id
    int id;
    //! Gear ratio for the motor's joint
    float gearRatio;

  public:
    Dynamixel(int idNumber, float ratio=1)
    {
      id = idNumber;
      gearRatio = ratio; 
    }

    ~Dynamixel()
    {
    }
  
    /** \brief Initialize Dynamixel servo motor and verify that it is reachable
      * \return success (bool)
      */
    bool init()
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
      dxl_wb.setMultiTurnControlMode(id);
      dxl_wb.setNormalDirection(id);
      setJointMode();
      dxl_wb.setMultiTurnControlMode(id);
      if(initSuccess && pingSuccess)
      {
        //Serial.print("Motor id: ");
        //Serial.print(id);
        //Serial.println(" has been initialized successfully") ;
        
        return true;
      }
      return false;
    }
    
    
    /** \brief Set the dynamixel in joint mode
      * \return success (bool)
      */
    bool setJointMode()
    {
      const char *log;
      bool result = false;
      result = dxl_wb.jointMode(id, 100, 0, &log);
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
    
    
    /** \brief Set the goal position of the dynamixel
      * \param pos : integer of the goal position
      */
    void moveMotor(int32_t pos)
    {
      int goalPos = pos * gearRatio;
      dxl_wb.goalPosition(id, goalPos);
      //Serial.println("Dynamixel is moving...");
    }

    /** \brief Get the current position of the Dynamixel
      * \return pos : integer of the current position
      */
    int32_t getPosition()
    {
      int32_t data;
      dxl_wb.getPresentPositionData(id, &data);
      uint16_t pos = data/gearRatio;
      return pos; 
    }
};
