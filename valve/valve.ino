#include <SoftwareSerial.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>


#define CLOSING_TIME 2000
#define CHAT_ID 968909687

StaticJsonBuffer<800> JSONbuffer;

ESP8266WiFiMulti WiFiMulti;

//Pins for controlling driver motor
int D1 = 5;
int D2 = 4;

int byteReceived = 0;

SoftwareSerial BTSerial(14, 12); // RX | TX

//BOT variables
const char *text;
int ID_int;
int message_ids[1] = {0};
bool value;
bool received = false;

void setup()
{
  // wifi initialization
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP("YouShallNotPass", "ushallnotpass");

  // driver motor pins initialization
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);

  // bluetoth initialization
  Serial.begin(9600);
  BTSerial.begin(38400);
}

void loop()
{
  if ((WiFiMulti.run() == WL_CONNECTED)) {

    std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);

    client->setFingerprint("BB DC 45 2A 07 E3 4A 71 33 40 32 DA BE 81 F7 72 6F 4A 2B 6B");

    HTTPClient https;

    if (https.begin(*client, "https://api.telegram.org/bot970539780:AAElJ4Gr1-BBcmBKHAL31yVg-SLYebt8Km8/getUpdates?allowed_updates=message&offset=-1&limit=1")) {
      int httpCode = https.GET();
      if (httpCode > 0) {
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = https.getString();

          JsonObject& root = JSONbuffer.parseObject(payload);
          text = root["result"][0]["message"]["text"];

          ID_int = atoi(root["result"][0]["message"]["message_id"]);

          JSONbuffer.clear();
        }
      }
      https.end();
    }
  }
  if (String(text) == "/start" && ID_int != message_ids[0]) {
    message_ids[0] = ID_int;

    JsonObject& JSONtext1 = JSONbuffer.createObject();
    JSONtext1["text"] = "Close valve";

    //    JsonObject& JSONtext2 = JSONbuffer.createObject();
    //    JSONtext2["text"] = "Sensor state";

    JsonObject& JSONencoder = JSONbuffer.createObject();
    JsonObject& JSONencoder1 = JSONbuffer.createObject();

    JsonArray& keyboard = JSONencoder1.createNestedArray("keyboard");

    JsonArray& keyboard1 = keyboard.createNestedArray();
    JsonArray& keyboard2 = keyboard.createNestedArray();
    keyboard1.add(JSONtext1);
    //    keyboard2.add(JSONtext2);

    JSONencoder["chat_id"] = CHAT_ID;
    JSONencoder["text"] = "Hi";

    JSONencoder["reply_markup"] = JSONencoder1;

    char JSONmessageBuffer[300];
    JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));

    Serial.println(JSONmessageBuffer);
    JSONbuffer.clear();
    post(JSONmessageBuffer);
  } else if (String(text) == "Close valve" && ID_int != message_ids[0]) {
    message_ids[0] = ID_int;
    value = true;
    close_valve();
    JsonObject& JSONencoder = JSONbuffer.createObject();
    JSONencoder["chat_id"] = CHAT_ID;
    JSONencoder["text"] = "Valve closed";

    char JSONmessageBuffer[300];
    JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
    JSONbuffer.clear();
    post(JSONmessageBuffer);
  }
  //  if (String(text) == "Sensor state" && ID_int != message_ids[0]) {
  //    message_ids[0] = ID_int;
  //
  //    JsonObject& JSONencoder = JSONbuffer.createObject();
  //    JSONencoder["chat_id"] = CHAT_ID;
  //    JSONencoder["text"] = "Kitchen: Good, Last seen: 2 min ago";
  //
  //    char JSONmessageBuffer[300];
  //    JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  //
  //    post(JSONmessageBuffer);
  //  }


  if (BTSerial.available()) {
//    byteReceived = 0;
    byteReceived = 0;;
    if (BTSerial.read() && !received) {
      close_valve();
      received = true;
      JsonObject& JSONencoder = JSONbuffer.createObject();
      JSONencoder["chat_id"] = CHAT_ID;
      JSONencoder["text"] = "Gas leackage, valve was closed";

      char JSONmessageBuffer[300];
      JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));

      post(JSONmessageBuffer);
    }
  }
}



void close_valve() {
  digitalWrite(D1, LOW);
  digitalWrite(D2, HIGH);
  delay(CLOSING_TIME);
  stop_rotation();
}
void stop_rotation() {
  digitalWrite(D1, LOW);
  digitalWrite(D2, LOW);

}

void post(char *message) {
  if ((WiFiMulti.run() == WL_CONNECTED)) {

    std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);

    client->setFingerprint("BB DC 45 2A 07 E3 4A 71 33 40 32 DA BE 81 F7 72 6F 4A 2B 6B");

    HTTPClient https;


    if (https.begin(*client, "https://api.telegram.org/bot970539780:AAElJ4Gr1-BBcmBKHAL31yVg-SLYebt8Km8/sendMessage")) {  // HTTPS
      https.addHeader("Content-Type", "application/json");
      https.POST(message);
      https.end();
    }
    JSONbuffer.clear();
  }
}
