/*
    Ahsan Habib (habib@deakin.edu.au),
    School of Information Technology,
    Deakin University, Australia.
*/

int x;

void setup() {
  Serial.begin(9600);  // set baud rate
}

void loop() {
  while (!Serial.available()) {} // wait for data to arrive

  // read string data from Serial, we know Python 
  // script is sending just an integer.
  x = Serial.readString().toInt();

  // write a string (no newline)
  Serial.print("Arduino sends: ");  

  // Add 1 to what received.
  // Write an integer with a newline (println vs print).
  Serial.println(x + 1);  

  // Push the data through serial channel.
  Serial.flush();  
}
