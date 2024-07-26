#include <Arduino.h>

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    int blinks = Serial.parseInt();
    for (int i = 0; i < blinks; i++) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);
      digitalWrite(LED_BUILTIN, LOW);
      delay(1000);
    }
    int waitTime = random(1, 10);  // Send a random wait time between 1 and 10 seconds
    Serial.println(waitTime);
  }
}


