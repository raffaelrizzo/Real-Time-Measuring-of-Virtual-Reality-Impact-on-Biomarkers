#include <ArduinoJson.h>


const int capacity = JSON_OBJECT_SIZE(1);

StaticJsonDocument<capacity> doc;

int min = 2048, max = -2048;

double read_normalized(){
  int value1 = analogRead(A4);
  if (value1 > max){
    max = value1;
  }
  if (value1 < min){
    min = value1;
  }
  return (double)(value1 - min) / (max-min);
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  for (int i=0; i < 100; i++){
    read_normalized();
  }
}



void loop() {
  doc["v1"] = read_normalized();
  serializeJson(doc, Serial);
  Serial.println();
}