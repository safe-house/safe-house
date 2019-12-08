#include "Adafruit_CCS811.h"
#include <SoftwareSerial.h>

SoftwareSerial MyBlue(8, 9); // RX | TX

uint16_t eCO2, TVOC;

Adafruit_CCS811 ccs;

void setup() {
  Serial.begin(9600);
  MyBlue.begin(38400);

  if (!ccs.begin()) {
    Serial.println("Failed to start sensor! Please check your wiring.");
    while (1);
  }

  // Wait for the sensor to be ready
  while (!ccs.available());
}

void loop() {
  if (ccs.available()) {
    if (!ccs.readData()) {
      eCO2 = ccs.geteCO2();
      TVOC = ccs.getTVOC();
            Serial.print(eCO2);
      if ( eCO2 > 1500 ){
        MyBlue.write(1);
      }

    }
    else {
      Serial.println("ERROR!");
    }
  }
  
  delay(1000);
}
