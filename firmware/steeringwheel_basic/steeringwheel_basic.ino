const int potPin = A0; // Potentiometer connected to A0 on ESP8266
const int numReadings = 10; // Number of readings for smoothing

int readings[numReadings];  // Array to store potentiometer readings
int readIndex = 0;          // Index for the current reading
int total = 0;              // Total of readings
int average = 0;            // Smoothed value

void setup() {
    Serial.begin(115200);   // Start Serial communication  
    pinMode(potPin, INPUT); // Set A0 as input for the potentiometer

    // Initialize the readings array
    for (int i = 0; i < numReadings; i++) {
        readings[i] = 0;
    }
}

void loop() {
    total -= readings[readIndex];         // Subtract the last reading
    readings[readIndex] = analogRead(potPin); // Get the current reading
    total += readings[readIndex];         // Add the current reading to total

    readIndex++;                          // Advance to the next index
    if (readIndex >= numReadings) {       // If we've reached the end of the array, reset index
        readIndex = 0;
    }

    average = total / numReadings;        // Calculate the smoothed average

    Serial.print("Smoothed Potentiometer Value: ");
    Serial.println(average); // Print the smoothed value

    delay(10); // Small delay for stability (adjust as needed)
}
