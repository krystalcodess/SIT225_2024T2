#include "arduino_secrets.h"
#include "thingProperties.h"
#include <DHT.h>

#define DHTPIN 2     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22 (AM2302)

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

bool wifiConnected = false;

void setup() {
  Serial.begin(9600);
  delay(1500); 

  // This function initializes the connection to the IoT Cloud
  initProperties();

  // Connect to Arduino IoT Cloud
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);

  setDebugMessageLevel(1);  // Reduced debug level
  ArduinoCloud.printDebugInfo();

  dht.begin();
}

void loop() {
  // Check WiFi connection
  if (ArduinoIoTPreferredConnection.check() != NetworkConnectionState::CONNECTED) {
    if (wifiConnected) {
      Serial.println("WiFi connection lost. Reconnecting...");
      wifiConnected = false;
    }
    ArduinoIoTPreferredConnection.connect();
  } else if (!wifiConnected) {
    Serial.println("WiFi connected!");
    wifiConnected = true;
  }

  // Execute the cloud functions
  ArduinoCloud.update();

  // Read humidity and temperature from the DHT22 sensor
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    return;
  }

  // Update the properties
  humid = h;
  temp = t;

  // Print the values to serial monitor (for debugging)
  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println(" *C");

  // Wait a few seconds between measurements.
  delay(2000);
}

void onHumidChange()  {
  // Add your code here to act upon Humid change
}

void onTempChange()  {
  // Add your code here to act upon Temp change
}