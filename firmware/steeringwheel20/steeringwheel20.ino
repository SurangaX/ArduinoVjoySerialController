const int potPin = A0;      // Potentiometer connected to A0 on ESP8266     
const int buttonPin3 = D5;  // Button 3 connected to D5 on ESP8266
const int buttonPin1 = D1;  // Button 1 connected to D1 on ESP8266
const int buttonPin2 = D2;  // Button 2 connected to D2 on ESP8266
const int buttonPin5 = D6;  // Button 4 connected to D6 on ESP8266
const int buttonPin4 = D7;  // Button 5 connected to D7 on ESP8266
const int buttonPin6 = D0;   // Button 6 connected to GPIO3 (RX pin)

const int numReadings = 10;  // Number of readings for smoothing

int readings[numReadings];   // Array to store potentiometer readings
int readIndex = 0;           // Index for the current reading
int total = 0;               // Total of readings
int average = 0;             // Smoothed value
bool lastButtonState1 = LOW; // Previous state for button 1
bool lastButtonState2 = LOW; // Previous state for button 2
bool lastButtonState3 = LOW; // Previous state for button 3
bool lastButtonState4 = LOW; // Previous state for button 4
bool lastButtonState5 = LOW; // Previous state for button 5
bool lastButtonState6 = LOW; // Previous state for button 6
unsigned long lastDebounceTime1 = 0; // Last time button 1 was toggled
unsigned long lastDebounceTime2 = 0; // Last time button 2 was toggled
unsigned long lastDebounceTime3 = 0; // Last time button 3 was toggled
unsigned long lastDebounceTime4 = 0; // Last time button 4 was toggled
unsigned long lastDebounceTime5 = 0; // Last time button 5 was toggled
unsigned long lastDebounceTime6 = 0; // Last time button 6 was toggled
unsigned long debounceDelay = 50; // Debounce time in milliseconds

void setup() {
    Serial.begin(115200);   // Start Serial communication  
    pinMode(potPin, INPUT); // Set A0 as input for the potentiometer
    pinMode(buttonPin1, INPUT_PULLUP); // Set D1 as input for button 1 with internal pull-up
    pinMode(buttonPin2, INPUT_PULLUP); // Set D2 as input for button 2 with internal pull-up
    pinMode(buttonPin3, INPUT_PULLUP); // Set D5 as input for button 3 with internal pull-up
    pinMode(buttonPin4, INPUT_PULLUP); // Set D7 as input for button 4 with internal pull-up
    pinMode(buttonPin5, INPUT_PULLUP); // Set D6 as input for button 5 with internal pull-up
    pinMode(buttonPin6, INPUT_PULLUP); // Set GPIO3 (RX) as input for button 6 with internal pull-up

    // Initialize the readings array
    for (int i = 0; i < numReadings; i++) {
        readings[i] = 0;
    }
}

void loop() {
    // Read the button states
    int buttonState1 = digitalRead(buttonPin1); // Read the state of button 1
    int buttonState2 = digitalRead(buttonPin2); // Read the state of button 2
    int buttonState3 = digitalRead(buttonPin3); // Read the state of button 3
    int buttonState4 = digitalRead(buttonPin4); // Read the state of button 4
    int buttonState5 = digitalRead(buttonPin5); // Read the state of button 5
    int buttonState6 = digitalRead(buttonPin6); // Read the state of button 6

    // Check for button 1 press with debounce
    if (buttonState1 != lastButtonState1) {
        lastDebounceTime1 = millis(); // Reset the debounce timer for button 1
    }
    if ((millis() - lastDebounceTime1) > debounceDelay) {
        if (buttonState1 == LOW) { // Button 1 pressed (active LOW)
            Serial.println("Button 1 pressed!");
        } else {
            Serial.println("Button 1 released!");
        }
    }
    lastButtonState1 = buttonState1; // Save the current state for button 1

    // Check for button 2 press with debounce
    if (buttonState2 != lastButtonState2) {
        lastDebounceTime2 = millis(); // Reset the debounce timer for button 2
    }
    if ((millis() - lastDebounceTime2) > debounceDelay) {
        if (buttonState2 == LOW) {
            Serial.println("Button 2 pressed!");
        } else {
            Serial.println("Button 2 released!");
        }
    }
    lastButtonState2 = buttonState2; // Save the current state for button 2

    // Repeat the same debounce logic for buttons 3, 4, 5, and 6
    // Button 3
    if (buttonState3 != lastButtonState3) {
        lastDebounceTime3 = millis();
    }
    if ((millis() - lastDebounceTime3) > debounceDelay) {
        if (buttonState3 == LOW) {
            Serial.println("Button 3 pressed!");
        } else {
            Serial.println("Button 3 released!");
        }
    }
    lastButtonState3 = buttonState3;

    // Button 4
    if (buttonState4 != lastButtonState4) {
        lastDebounceTime4 = millis();
    }
    if ((millis() - lastDebounceTime4) > debounceDelay) {
        if (buttonState4 == LOW) {
            Serial.println("Button 4 pressed!");
        } else {
            Serial.println("Button 4 released!");
        }
    }
    lastButtonState4 = buttonState4;

    // Button 5
    if (buttonState5 != lastButtonState5) {
        lastDebounceTime5 = millis();
    }
    if ((millis() - lastDebounceTime5) > debounceDelay) {
        if (buttonState5 == LOW) {
            Serial.println("Button 5 pressed!");
        } else {
            Serial.println("Button 5 released!");
        }
    }
    lastButtonState5 = buttonState5;

    // Button 6 (GPIO3 - RX pin)
    if (buttonState6 != lastButtonState6) {
        lastDebounceTime6 = millis();
    }
    if ((millis() - lastDebounceTime6) > debounceDelay) {
        if (buttonState6 == LOW) {
            Serial.println("Button 6 pressed!");
        } else {
            Serial.println("Button 6 released!");
        }
    }
    lastButtonState6 = buttonState6;

    // Potentiometer reading and smoothing
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

    delay(50); // Small delay for stability (adjust as needed)
}
