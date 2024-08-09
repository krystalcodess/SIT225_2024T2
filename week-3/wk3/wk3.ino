#include "thingProperties.h"

void setup() {
  // Initialize serial and wait for port to open:
  Serial.begin(9600);
  // This delay gives the chance to wait for a Serial Monitor without blocking if none is found
  delay(1500); 

  // Defined in thingProperties.h
  initProperties();

  // Connect to Arduino IoT Cloud
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);
  
  /*
     The following function allows you to obtain more information
     related to the state of network and IoT Cloud connection and errors
     the higher number the more granular information you’ll get.
     The default is 0 (only errors).
     Maximum is 4
 */
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();
}

void loop() {
  ArduinoCloud.update();
  // Your code here 
  randomTemperature = 1.0 * random(1, 100);
  Serial.println("random temperature: " + String(randomTemperature));
  delay(5*1000);
}

/*
  Since Temperature is READ_WRITE variable, onRandomTemperatureChange() is
  executed every time a new value is received from IoT Cloud.
*/
void onRandomTemperatureChange()  {
  // Add your code here to act upon Temperature change
  Serial.println("--onRandomTemperatureChange");
}