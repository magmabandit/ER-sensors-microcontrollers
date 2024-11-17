/** Steering sensor (novotech PF2C1 potentiometer) measurer program
 *  Power off 5V & GND. Wiper pin to READERPIN. Prints out value as angle
 *  note that with axle facing you, angle is actually read counterclockwise;
 * e.g. with 0 degrees facing North, 90 degrees is West
 */
const int READERPIN = A0;

void setup()
{
  // put your setup code here, to run once:
  pinMode(READERPIN, INPUT);
  Serial.begin(115200);
}

void loop()
{
  // put your main code here, to run repeatedly:
  int reading = analogRead(READERPIN);
  int voltage = map(reading, 0, 1023, 0, 360);
  Serial.println(voltage);
}
