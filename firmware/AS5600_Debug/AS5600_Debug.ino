#include <Wire.h>
#include <AS5600.h> // Library by Rob Tillaart

AS5600 as5600;

void setup() {
    Serial.begin(115200);
    Wire.begin(D2, D1);      // SDA = D2, SCL = D1
    Wire.setClock(100000);   // 100kHz - safer for 2ft cable (default 400kHz too fast)

    Serial.println("=== AS5600 Sensor Debug ===");

    if (!as5600.isConnected()) {
        Serial.println("ERROR: AS5600 NOT detected on I2C! Check wiring.");
    } else {
        Serial.println("AS5600 CONNECTED OK!");
        Serial.print("Magnet strength: ");
        Serial.println(as5600.readMagnitude());
    }
}

void loop() {
    if (as5600.isConnected()) {
        int rawAngle = as5600.readAngle();  // 0 - 4095
        float degrees = rawAngle * (360.0 / 4096.0);

        Serial.print("Raw: ");
        Serial.print(rawAngle);
        Serial.print("  |  Degrees: ");
        Serial.println(degrees, 1);
    } else {
        Serial.println("ERROR: AS5600 disconnected!");
    }

    delay(100); // 10 times per second
}
