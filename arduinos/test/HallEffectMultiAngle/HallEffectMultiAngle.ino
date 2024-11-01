/*
Hall-Effect Multi-Angle Reader
Name: Charlotte Wong, Phuong Dao, Andre Chabra, Kerem Deniz Ozturk
Date: 10/31/2024
Description: Reads in data from 2 Hall Effect sensors, 
which are plugged into an arduino, plugged into computer. 
Voltage output is converted to angle from -45 to 45 &
printed out to serial.

I got rid of the code for the LED because all it did was
change the built in LED and doesn't contribute to our needs
*/

int HallSensor = A0; // analog pin numbers
int HallSensor2 = A5;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(HallSensor, INPUT);
  pinMode(HallSensor2, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1);

  int sensorStatus = analogRead(HallSensor);
  int sensorStatus2 = analogRead(HallSensor2);

  long voltage = map(sensorStatus, 0, 1023, 0, 5000); //in millivolts
  long angle = map(voltage, 440, 4540, -45 , 46);

  long voltage2 = map(sensorStatus2, 0, 1023, 0, 5000); //in millivolts
  long angle2 = map(voltage2, 440, 4540, -45 , 46);

  // first prints out the angle from the Hall Effect Sensor plugged into A0
  // and then prints out the angle from the Hall Effect Sensor plugged into A5
  // aka the left number in the monitor is from A0 and the right number is from A5
  // I use Serial.print for the first angle and the comma so that way
  // everything stays on the same line when it gets printed
  Serial.print(angle);
  Serial.print(", ");
  Serial.println(angle2);

}
