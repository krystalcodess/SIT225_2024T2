#include "arduino_secrets.h"
#include "Arduino_LSM6DS3.h"
#include "ArduinoIoTCloud.h"
#include "Arduino_ConnectionHandler.h"
#include "arduino_secrets.h"

const char DEVICE_LOGIN_NAME[]  = "YourDeviceLoginName";
const char DEVICE_KEY[]  = "YourDeviceKey";

void onAlarmTriggeredChange();
void onAlarmSeverityChange();

bool alarm_triggered;
float alarm_severity;

void initProperties() {
  ArduinoCloud.addProperty(alarm_triggered, READWRITE, ON_CHANGE, onAlarmTriggeredChange);
  ArduinoCloud.addProperty(alarm_severity, READWRITE, ON_CHANGE, onAlarmSeverityChange);
}

WiFiConnectionHandler ArduinoIoTPreferredConnection(SECRET_SSID, SECRET_OPTIONAL_PASS);

// Alarm detection parameters
const int SAMPLES = 50;  // 500ms at 100Hz
const float THRESHOLD = 2.5;  // in g's
const int CONSECUTIVE_SAMPLES = 5;
const unsigned long ALARM_DURATION = 5000;  // 5 seconds

float accelMagnitude[SAMPLES];
int sampleIndex = 0;
unsigned long alarmStartTime = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  initProperties();
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  alarm_triggered = true;
  alarm_severity = 0;

  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();
}

void loop() {
  ArduinoCloud.update();
  
  float x, y, z;
  
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    
    // Calculate magnitude
    float magnitude = sqrt(x*x + y*y + z*z);
    
    // Store in circular buffer
    accelMagnitude[sampleIndex] = magnitude;
    sampleIndex = (sampleIndex + 1) % SAMPLES;
    
    // Check for alarm condition
    int highMagSamples = 0;
    float maxMagnitude = 0;
    for (int i = 0; i < SAMPLES; i++) {
      if (accelMagnitude[i] > THRESHOLD) {
        highMagSamples++;
        if (accelMagnitude[i] > maxMagnitude) {
          maxMagnitude = accelMagnitude[i];
        }
        if (highMagSamples >= CONSECUTIVE_SAMPLES && !alarm_triggered) {
          alarm_triggered = true;
          alarmStartTime = millis();
          break;
        }
      } else {
        highMagSamples = 0;
      }
    }
    
    // Calculate alarm severity
    if (alarm_triggered) {
      alarm_severity = 100.0 * (maxMagnitude - THRESHOLD) / (THRESHOLD * 2);
      alarm_severity = constrain(alarm_severity, 0, 100);
    } else {
      alarm_severity = 0;
    }
    
    // Reset alarm after duration
    if (alarm_triggered && (millis() - alarmStartTime > ALARM_DURATION)) {
      alarm_triggered = false;
      alarm_severity = 0;
    }
  }
  
  delay(10);  // Approximately 100Hz sampling rate
}

void onAlarmTriggeredChange() {
  Serial.print("Alarm Triggered changed to: ");
  Serial.println(alarm_triggered);
}

void onAlarmSeverityChange() {
  Serial.print("Alarm Severity changed to: ");
  Serial.println(alarm_severity);
}