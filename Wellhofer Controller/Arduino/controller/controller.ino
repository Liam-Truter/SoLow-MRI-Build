const int analogPin = A0;     // Pin connected to the voltage divider midpoint
const int thresholdResistance = 1000;  // 1kΩ threshold
const int fixedResistance = 2200;      // 1kΩ fixed resistor value
const int digitalPin2 = 2;    // Pin to set high if variable resistor > 1kΩ
const int digitalPin3 = 3;    // Pin to set high if variable resistor <= 1kΩ

void setup() {
  pinMode(digitalPin2, OUTPUT);
  pinMode(digitalPin3, OUTPUT);
  Serial.begin(9600);         // Initialize serial communication for debugging
}

void loop() {
  int sensorValue = analogRead(analogPin);  // Read analog input on A0
  float voltage = sensorValue * (5.0 / 1023.0);  // Convert to voltage (0-5V range)

  // Calculate the resistance of the variable resistor (R2) using the voltage divider formula
  float variableResistance = voltage/(5-voltage)*fixedResistance;

  // Output resistance to Serial Monitor for debugging
  Serial.print("POS: ");
  Serial.print(variableResistance);
  Serial.print(" ");
  Serial.print(0.0);
  Serial.print(" ");
  Serial.println(0.0);

  // Compare resistance with the threshold and set digital pins
  if (variableResistance > thresholdResistance) {
    digitalWrite(digitalPin2, HIGH);  // Set D2 high if R2 > 1kΩ
    digitalWrite(digitalPin3, LOW);
  } else {
    digitalWrite(digitalPin2, LOW);
    digitalWrite(digitalPin3, HIGH);  // Set D3 high if R2 <= 1kΩ
  }

  delay(100);  // Delay for readability in Serial Monitor
}

