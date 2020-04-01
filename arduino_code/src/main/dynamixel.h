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
      dxl_wb.setNormalDirection(id);
      setOperatingMode();
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
    bool setOperatingMode()
    {
      const char *log;
      bool result = false;
      //result = dxl_wb.jointMode(id, 150, 10, &log);
      result = dxl_wb.setExtendedPositionControlMode(id ,&log);
      //Serial.println(log);
      dxl_wb.writeRegister(id,"Profile_Acceleration",10,&log);
      //Serial.println(log);
      dxl_wb.writeRegister(id,"Profile_Velocity",150,&log);
      dxl_wb.torqueOn(id);
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
      int32_t goalPos = pos * gearRatio;
      dxl_wb.goalPosition(id, (int32_t)goalPos);
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

    void torque(bool onoff)
    {
      
      dxl_wb.torque(id, onoff);
    }
};
