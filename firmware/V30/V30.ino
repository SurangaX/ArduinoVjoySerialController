#include <Wire.h>
#include <AS5600.h> // Library by Rob Tillaart

AS5600 as5600;

// --- MULTI-TURN TRACKING VARIABLES ---
long continuousAngle = 0;
int lastRawAngle = -1;
int errorCount = 0;

// --- POTENTIOMETER VARIABLES ---
const int potPin = A0;
float emaPotValue = 0;
const float emaAlpha = 0.2; // Smoothing factor (0.0 - 1.0)

// --- PIN DEFINITIONS ---
// Sensor MUST be on D1 (SCL) and D2 (SDA)
const int buttonPin1 = D4;  // Button 1 on D4 (Don't press during boot!)
const int buttonPin2 = 3;   // Button 2 on RX pin (GPIO3)
const int buttonPin3 = D5;  // Button 3 on D5
const int buttonPin4 = D7;  // Button 4 on D7
const int buttonPin5 = D6;  // Button 5 on D6
const int buttonPin6 = D0;  // Button 6 on D0

// Button state tracking (for debouncing)
int buttonState1 = HIGH;
int buttonState2 = HIGH;
int buttonState3 = HIGH;
int buttonState4 = HIGH;
int buttonState5 = HIGH;
int buttonState6 = HIGH;

int lastButtonState1 = HIGH;
int lastButtonState2 = HIGH;
int lastButtonState3 = HIGH;
int lastButtonState4 = HIGH;
int lastButtonState5 = HIGH;
int lastButtonState6 = HIGH;

unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;
unsigned long lastDebounceTime3 = 0;
unsigned long lastDebounceTime4 = 0;
unsigned long lastDebounceTime5 = 0;
unsigned long lastDebounceTime6 = 0;
const unsigned long debounceDelay = 50;

void setup() {
    Serial.begin(115200);   
    
    // Initialize I2C for AS5600 on the safe pins (SDA = D2, SCL = D1)
    Wire.begin(D2, D1);
    as5600.begin(); // Initialize the Rob Tillaart library
    
    // Setup button pins
    pinMode(buttonPin1, INPUT_PULLUP);
    // Note: RX pin is GPIO3, we set it as input
    pinMode(buttonPin2, INPUT_PULLUP); 
    pinMode(buttonPin3, INPUT_PULLUP);
    pinMode(buttonPin4, INPUT_PULLUP);
    pinMode(buttonPin5, INPUT_PULLUP);
    pinMode(buttonPin6, INPUT_PULLUP);
    
    Serial.println("V30 AS5600 Wheel Initialized");
    
    if (!as5600.isConnected()) {
        Serial.println("WARNING: AS5600 not detected on I2C bus!");
    } else {
        // Apply hardware filters
        as5600.setSlowFilter(0);
        as5600.setFastFilter(7);
        as5600.setHysteresis(3);
        
        // Initialize multi-turn tracking
        lastRawAngle = as5600.readAngle();
        continuousAngle = lastRawAngle;
    }
}

void loop() {
    // Read the current pin states
    int read1 = digitalRead(buttonPin1);
    int read2 = digitalRead(buttonPin2);
    int read3 = digitalRead(buttonPin3);
    int read4 = digitalRead(buttonPin4);
    int read5 = digitalRead(buttonPin5);
    int read6 = digitalRead(buttonPin6);

    // --- BUTTON DEBOUNCE LOGIC ---
    
    // Button 1
    if (read1 != lastButtonState1) lastDebounceTime1 = millis();
    if ((millis() - lastDebounceTime1) > debounceDelay) {
        if (read1 != buttonState1) {
            buttonState1 = read1;
            if (buttonState1 == LOW) Serial.println("Button 1 pressed!");
            else Serial.println("Button 1 released!");
        }
    }
    lastButtonState1 = read1;

    // Button 2
    if (read2 != lastButtonState2) lastDebounceTime2 = millis();
    if ((millis() - lastDebounceTime2) > debounceDelay) {
        if (read2 != buttonState2) {
            buttonState2 = read2;
            if (buttonState2 == LOW) Serial.println("Button 2 pressed!");
            else Serial.println("Button 2 released!");
        }
    }
    lastButtonState2 = read2;

    // Button 3
    if (read3 != lastButtonState3) lastDebounceTime3 = millis();
    if ((millis() - lastDebounceTime3) > debounceDelay) {
        if (read3 != buttonState3) {
            buttonState3 = read3;
            if (buttonState3 == LOW) Serial.println("Button 3 pressed!");
            else Serial.println("Button 3 released!");
        }
    }
    lastButtonState3 = read3;

    // Button 4
    if (read4 != lastButtonState4) lastDebounceTime4 = millis();
    if ((millis() - lastDebounceTime4) > debounceDelay) {
        if (read4 != buttonState4) {
            buttonState4 = read4;
            if (buttonState4 == LOW) Serial.println("Button 4 pressed!");
            else Serial.println("Button 4 released!");
        }
    }
    lastButtonState4 = read4;

    // Button 5
    if (read5 != lastButtonState5) lastDebounceTime5 = millis();
    if ((millis() - lastDebounceTime5) > debounceDelay) {
        if (read5 != buttonState5) {
            buttonState5 = read5;
            if (buttonState5 == LOW) Serial.println("Button 5 pressed!");
            else Serial.println("Button 5 released!");
        }
    }
    lastButtonState5 = read5;

    // Button 6
    if (read6 != lastButtonState6) lastDebounceTime6 = millis();
    if ((millis() - lastDebounceTime6) > debounceDelay) {
        if (read6 != buttonState6) {
            buttonState6 = read6;
            if (buttonState6 == LOW) Serial.println("Button 6 pressed!");
            else Serial.println("Button 6 released!");
        }
    }
    lastButtonState6 = read6;

    // --- AS5600 SENSOR READING ---
    if (as5600.isConnected()) {
        int rawAngle = as5600.readAngle();
        
        if (lastRawAngle == -1) {
            lastRawAngle = rawAngle;
            continuousAngle = rawAngle;
        } else {
            int diff = rawAngle - lastRawAngle;
            
            if (abs(diff) > 200) {
                // If the jump is massive (e.g. 4095 to 0), it's a boundary crossing
                if (diff < -2000) {
                    diff += 4096;
                } else if (diff > 2000) {
                    diff -= 4096;
                }
                
                // Only ignore if it's a small jitter spike (not a full rotation)
                bool isDirFlip = abs(rawAngle + lastRawAngle - 4096) < 20;
                
                if ((abs(diff) > 250 || isDirFlip) && errorCount < 5) {
                    errorCount++;
                } else {
                    errorCount = 0;
                    continuousAngle += diff;
                    lastRawAngle = rawAngle;
                    
                    // Send the raw continuous multi-turn angle to Python
                    Serial.print("AS5600 Angle: ");
                    Serial.println(continuousAngle);
                }
            } else {
                lastRawAngle = rawAngle;
                continuousAngle += diff;
                
                Serial.print("AS5600 Angle: ");
                Serial.println(continuousAngle);
            }
        }
    }
    
    // --- POTENTIOMETER READING ---
    int rawPot = analogRead(potPin);
    if (emaPotValue == 0) {
        emaPotValue = rawPot; // Initialize on first read
    } else {
        emaPotValue = (emaAlpha * rawPot) + ((1.0 - emaAlpha) * emaPotValue);
    }
    Serial.print("Smoothed Potentiometer Value: ");
    Serial.println((int)emaPotValue);
    
    // Run at ~50Hz (20ms delay), fast enough for gaming
    delay(20); 
}
