#include <NewPing.h>

const int trig = 12;
const int echo = 13;
const int LED1 = 2; // Green 1
const int LED2 = 3; // Green 2
const int LED3 = 4; // Yellow
const int LED4 = 5; // Red 1
const int LED5 = 6; // Red 2

NewPing sonar(trig, echo, 200); 

void setup() {
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  delay(50); // Wait 50ms between pings (about 20 pings/sec)
  
  int distance = sonar.ping_cm();
  
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // LED control based on the specified distances
  if (distance > 40) {
    controlLEDs(HIGH, LOW, LOW, LOW, LOW); // Green 1 (LED1) is ON
  }
  else if (distance > 30 && distance <= 40) {
    controlLEDs(LOW, HIGH, LOW, LOW, LOW); // Green 2 (LED2) is ON
  }
  else if (distance > 20 && distance <= 30) {
    controlLEDs(LOW, LOW, HIGH, LOW, LOW); // Yellow (LED3) is ON
  }
  else if (distance > 10 && distance <= 20) {
    controlLEDs(LOW, LOW, LOW, HIGH, LOW); // Red 1 (LED4) is ON
  }
  else if (distance <= 10) {
    controlLEDs(LOW, LOW, LOW, LOW, HIGH); // Red 2 (LED5) is ON
  } else {

    controlLEDs(LOW, LOW, LOW, LOW, LOW);
  }
  
  Serial.println("--------------------");
  delay(1000); 
}

// Helper function to control all LEDs at once
void controlLEDs(int led1State, int led2State, int led3State, int led4State, int led5State) {
  digitalWrite(LED1, led1State);
  digitalWrite(LED2, led2State);
  digitalWrite(LED3, led3State);
  digitalWrite(LED4, led4State);
  digitalWrite(LED5, led5State);
  
  // Debug information
  Serial.print("LED1 (Green 1): ");
  Serial.println(led1State == HIGH ? "ON" : "OFF");
  
  Serial.print("LED2 (Green 2): ");
  Serial.println(led2State == HIGH ? "ON" : "OFF");
  
  Serial.print("LED3 (Yellow): ");
  Serial.println(led3State == HIGH ? "ON" : "OFF");
  
  Serial.print("LED4 (Red 1): ");
  Serial.println(led4State == HIGH ? "ON" : "OFF");
  
  Serial.print("LED5 (Red 2): ");
  Serial.println(led5State == HIGH ? "ON" : "OFF");
}

