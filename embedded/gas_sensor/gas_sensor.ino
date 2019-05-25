#include <SoftwareSerial.h>

#define SSerialRX        8
#define SSerialTX        9

#define SSerialTxControl 2

#define RS485Transmit    HIGH
#define RS485Receive     LOW

#define input         A4
#define LED           5

SoftwareSerial RS485Serial(SSerialRX, SSerialTX);

int byteReceived;
int byteSend;
float sensorValue;
float sensorVoltage;


void setup()
{
  Serial.begin(9600);

  pinMode(SSerialTxControl, OUTPUT);
  pinMode(LED, OUTPUT);

  digitalWrite(SSerialTxControl, RS485Transmit);

  RS485Serial.begin(4800);
}


void loop()
{
  sensorValue = analogRead(input);
  sensorVoltage = sensorValue / 1024 * 5.0;
  if (sensorVoltage > 1) {
    RS485Serial.write(1);
    delay(10);
    digitalWrite(LED, HIGH);
  }
  else {
    digitalWrite(LED, LOW);
  }
  delay(500);
}
