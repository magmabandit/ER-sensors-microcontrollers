// Breaklights + Pump MOSFET Driver
// Alex Lee, 2/15/25
//
// Edited by Andre Chabra, 4/25/2025
//
// Drives (5V) to MOSFETs for Breaklights and Pump under
// certain conditions.

int pump_mosfet = 10;
int brake_mosfet = 11;

union FloatUnion {
    byte bytes[4];
    float value;
};

void setup() {
    Serial.begin(19200); 
    // pinMode(pump_mosfet, OUTPUT);
    pinMode(brake_mosfet, OUTPUT);
}

void loop() {
    static bool receiving = false;
    static byte buffer[4];
    int byteIndex = 0;
    int numFloats = 0;

    // get sensor readings from aggregator
    while (Serial.available()) {

        byte incomingByte = Serial.read();

        if (!receiving) {
            if (incomingByte == 0xFF) {  // Start marker detected
                receiving = true;
            }
            
        } else {
          if (incomingByte == 2) {
            FloatUnion reading1, reading2; // TODO: change to fit actual sensor readings
            // for (int j = 0; j < 4; j++) {
            //   while (!Serial.available());
            //   reading1.bytes[j] = Serial.read();
            // }

            for (int j = 0; j < 4; j++) {
              while (!Serial.available());
              reading2.bytes[j] = Serial.read();
            }

            // Pump
            // if (reading1.value == 0) { analogWrite(10, HIGH); } else { analogWrite(10, LOW);}
            // float motor_temp = reading1.value;
            // float threshold;
            // might need to re-map the temperature values to be in the full range of what the motorcontroller
            // can handle
            // long dutycycle = map(temp, 0, 3276, 0, 255);
            // dutycycle = constrain(dutycycle, 0, 255);
            // analogWrite(pump_mosfet, dutycycle);

            // basic version of temperature that turns on when the temp is at a certain value
            // and turns off when the temperature is below that value
            // if (motor_temp > threshold) {
            //   digitalWrite(pump_mosfet, HIGH);
            // // delay(100);
            // } else {
            //   digitalWrite(pump_mosfet, LOW);
            // }


            // Brake Pedal deprecated
            // long voltage = map(reading2.value, 0, 1023, 0, 5000);  //gets in millivolts
            // gets angle of the brake pedal from the voltage provided by the Raspberry Pi
            // might need to re-map the voltages to be in the full range of what the motorcontroller
            // can handle
            // long angle = map(reading2.value, 440, 4540, -45, 46);
            // angle = constrain(angle, -45, 46);

            // if the angle is greater than 5 degrees turn on the brake lights through mosfet
            // if (abs(angle) > 5) {
            // digitalWrite(brake_mosfet, HIGH);
            // // delay(100);
            // } else {
            //   digitalWrite(brake_mosfet, LOW);
            // }

            // Brake Pedal
            // discrete voltage values for brake light on/off are 2.5 on and  off
            float voltage = reading2.value;
            if (2.0 < voltage && voltage < 3.0) {
              digitalWrite(brake_mosfet, HIGH);
            // delay(100);
            } else {
              digitalWrite(brake_mosfet, LOW);
            }
          }
            // Template for reading a variable number of sensors:
            // -------------------------------------------------
            // for (int i = 0; i < numFloats; i++) {
            //     FloatUnion receivedFloat;

            //     for (int j = 0; j < 4; j++) {
            //         while (!Serial.available());
            //         receivedFloat.bytes[j] = Serial.read();
            //     }

            //     Serial.print("Received float: ");
            //     Serial.println(receivedFloat.value, 6);
            // }
            // -------------------------------------------------


            receiving = false; // Try to receive a new message
        }
    }
}
