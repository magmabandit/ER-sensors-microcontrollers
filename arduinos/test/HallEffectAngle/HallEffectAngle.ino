/*
Hall-Effect Angle Reader
Name: Charlotte Wong, Phuong Dao, Andre Chabra, Kerem Deniz Ozturk
Date: 10/20/2024
Description: Reads in data from Hall Effect sensor, 
which is plugged into arduino, plugged into computer. 
Voltage output is converted to angle from -45 to 45 &
printed out to serial.
*/

int HallSensor = A5;
int LED = 13;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(HallSensor, INPUT);
  pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1);

  int sensorStatus = analogRead(HallSensor);

  long voltage = map(sensorStatus, 0, 1023, 0, 5000); //in millivolts
  long angle = map(voltage, 440, 4540, -45 , 46);

  // float voltage = sensorStatus/1023.0 * 5.0;
  // Serial.print("Hall sensor reading voltage: \n");
  // Serial.println(voltage); //range 0.44 -  4.54
  // Serial.print("Hall Sensor Reading angle: \n");
  Serial.println(angle);

}
