// Breaklights + Pump MOSFET Driver
// Alex Lee, 2/15/25
//
// Drives (5V) to MOSFETs for Breaklights and Pump under
// certain conditions.

union FloatUnion {
    byte bytes[4];
    float value;
};

void setup() {
    Serial.begin(115200); 
    pinMode(12, OUTPUT);
    pinMode(13, OUTPUT);
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
                while (!Serial.available());  // Wait for length byte
                numFloats = Serial.read();
            }
        } else {
          if (numFloats == 2) {

            FloatUnion reading1, reading2; // TODO: change to fit actual sensor readings
            for (int j = 0; j < 4; j++) {
              while (!Serial.available());
              reading1.bytes[j] = Serial.read();
            }

            for (int j = 0; j < 4; j++) {
              while (!Serial.available());
              reading2.bytes[j] = Serial.read();
            }

            // idea: power MOSFETs under some condition
            if (reading1.value < 45) { digitalWrite(12, HIGH); } else { digitalWrite(12, LOW); }

            if (reading2.value < 100.1) { digitalWrite(13, HIGH); } else { digitalWrite(13, LOW); }
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
