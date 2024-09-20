
/*
Test Arduino Program : - )
Alexander Lee
9/20/2024
*/
int i = 0;

void setup() {
  Serial.println("Hello World");

  Serial.begin(9600);
}

void loop() {
  Serial.print("Hello ");
  Serial.println(i);
  i++;
  Serial.setTimeout(1000);
}
