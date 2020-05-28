#include <ArduinoJson.h>
#include <EEPROM.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h> 
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFiMulti.h>

#define BUTT 14

String json;
String sensor_json;

int count;

DynamicJsonDocument doc(2048);
DynamicJsonDocument sensor(1024);


//Defining Web Server
ESP8266WebServer server(80);
/* Configuration Variables for the AP name and IP. */
const char *ssid = "Test";
const char *password = "Password";
IPAddress ap_local_IP(192,168,1,1);
IPAddress ap_gateway(192,168,1,254);
IPAddress ap_subnet(255,255,255,0);

int butt_state;

ESP8266WiFiMulti WiFiMulti;
WiFiClient client;

String s_len;
String p_len;

String ssid_eeprom;
String password_eeprom;
String token_eeprom;

//Creating the input form
const char INDEX_HTML[] =
"<!DOCTYPE HTML>"
"<html>"
"<head>"
"<meta content=\"text/html; charset=ISO-8859-1\""
" http-equiv=\"content-type\">"
"<meta name = \"viewport\" content = \"width = device-width, initial-scale = 1.0, maximum-scale = 1.0, user-scalable=0\">"
"<title>Safehouse Web Form</title>"
"<style>"
"\"body { background-color: #808080; font-family: Arial, Helvetica, Sans-Serif; Color: #000000; }\""
"</style>"
"</head>"
"<body>"
"<h1>Safehouse Web Form</h1>"
"<FORM action=\"/\" method=\"post\">"
"<P>"
"<label>ssid:&nbsp;</label>"
"<input maxlength=\"30\" name=\"ssid\"><br>"
"<label>Password:&nbsp;</label>"
"<input maxlength=\"30\" name=\"Password\"><br>"
"<label>Code from dashboard:&nbsp;</label>"
"<input maxlength=\"6\" name=\"Dashboard\"><br>"
"<INPUT type=\"submit\" value=\"Send\"> <INPUT type=\"reset\">"
"</P>"
"</FORM>"
"</body>"
"</html>";

void clearEEPROM() {
  for (int i = 0; i < 512; i++) {
    EEPROM.write(i, 0);
  }
  EEPROM.commit();
}

void handleNotFound()
{
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET)?"GET":"POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i=0; i<server.args(); i++){
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  message +="<H2><a href=\"/\">go home</a></H2><br>";
  server.send(404, "text/plain", message);
}


void _get() {
  if ((WiFiMulti.run() == WL_CONNECTED)) {
    Serial.println("ok");
    HTTPClient https;

    if (https.begin(client, "http://40.71.36.211/dashboard/error/")) {  // HTTPS
      int httpCode = https.GET();
      if (httpCode > 0) {
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = https.getString();

          Serial.println(payload);
          Serial.println(1);
        }
      }
      https.end();
    }
  }
}

void setup() {
  delay(1000);
  Serial.begin(115200);//Starting serial comunication
  EEPROM.begin(512);//Starting and setting size of the EEPROM

  pinMode(BUTT, INPUT_PULLUP);
  pinMode(2, OUTPUT);
  digitalWrite(2, LOW);
  
  if (char(EEPROM.read(150)) == '1') {
      String sid;
      String pswd;
    
      char arr_ssid[5];
      char arr_passwd[16];
      
      for(int i = 0; i < 30; i++) {
        if(EEPROM.read(0 + i) != 0) {
          sid += char(EEPROM.read(0 + i)); 
        }
      }
    
      for(int j = 100; j < 130; j++) {
        if(EEPROM.read(j) != 0) {
          pswd += char(EEPROM.read(j)); 
        }
      }
    
    sid.toCharArray(arr_ssid, 5);
    pswd.toCharArray(arr_passwd, 16);
    // sid.trim();
     Serial.println(sid);
    // pswd.trim();
     Serial.println(pswd);
    
    Serial.println(sid.length());
    Serial.println(pswd.length());
    
    WiFi.mode(WIFI_STA);
    WiFiMulti.addAP(arr_ssid, arr_passwd);

    delay(3000);
 
    if ((WiFiMulti.run() == WL_CONNECTED)) {
        Serial.println("True");
      } else {
        Serial.println("False");
      }
  } else {
      Serial.println();
      Serial.print("Configuring access point...");
      Serial.print("Setting soft-AP ... ");
      WiFi.softAP(ssid, password);
      Serial.print("Soft-AP IP address = ");
      Serial.println(WiFi.softAPIP());
      
    
      /**IPAddress myIP = WiFi.softAPIP();
      Serial.print("AP IP address: ");
      Serial.println(myIP);**/
      //Configuring the web server
      server.on("/", handleRoot);
      server.onNotFound(handleNotFound);
      server.begin();
      Serial.println("HTTP server started"); 
      server.handleClient();
  }
}


void loop() {
  butt_state = digitalRead(BUTT);
  delay(300);

  if (butt_state == LOW) {
    digitalWrite(2, HIGH);
    clearEEPROM();
    delay(500);
    ESP.restart();
  }
  
  if (char(EEPROM.read(150)) == '1') {
    if(count == 0) {
      post(1);
      count++;
    } else {
      post(0);
    }
  } else {
    server.handleClient();//Checks for web server activit
  }
}



//Dealing with the call to root
void handleRoot() {
   if (server.hasArg("ssid") && server.hasArg("Password") && server.hasArg("Dashboard")) {//If all form fields contain data call handelSubmit()
    handleSubmit();
  }
  else {//Redisplay the form
    server.send(200, "text/html", INDEX_HTML);
  }
}



void handleSubmit(){//dispaly values and write to memmory
 String response="<p>The ssid is ";
 response += server.arg("ssid");
 response +="<br>";
 response +="And the password is ";
 response += server.arg("Password");
 response +="<br>";
 response +="Token succesfuly released ";
 response += server.arg("Dashboard");
 response +="<br>";
 response +="</P><BR>";
 response +="<H2><a href=\"/\">go home</a></H2><br>";

 server.send(200, "text/html", response);

 clearEEPROM();
 
 write_to_Memory(String(server.arg("ssid")),String(server.arg("Password")),String(server.arg("Dashboard")));
 
 delay(500);

  for(int i = 0; i < String(server.arg("ssid")).length(); i++) {
     ssid_eeprom += char(EEPROM.read(0 + i));
  }

  for(int j = 100; j < String(server.arg("Password")).length() + 100; j++) {
     password_eeprom += char(EEPROM.read(j));
  }

  for(int k = 200; k < String(server.arg("Dashboard")).length() + 200; k++) {
    token_eeprom += char(EEPROM.read(k));
  }

 Serial.println(ssid_eeprom);
 Serial.println(password_eeprom);
 Serial.println(token_eeprom);
 Serial.println(char(EEPROM.read(150)));

 delay(1000);
 ESP.restart();
 //calling function that writes data to memory
}
//Write data to memory
/**
 * We prepping the data strings by adding the end of line symbol I decided to use ";". 
 * Then we pass it off to the write_EEPROM function to actually write it to memmory
 */
void write_to_Memory(String s,String p, String d){
 write_EEPROM(s,0);
 write_EEPROM(p,100);
 write_EEPROM(d,200);
 write_EEPROM("1", 150);
 EEPROM.commit();
}
//write to memory
void write_EEPROM(String x,int pos) {
  for(int n = pos; n < x.length()+pos; n++){
     EEPROM.write(n, x[n-pos]);
  }
}

int EEPROM_int_read(int addr) {   
  byte raw[2];
  for(byte i = 0; i < 2; i++) {
    raw[i] = EEPROM.read(addr+i);
  }
  int &num = (int&)raw;
  return num - 1;
}
 
void EEPROM_int_write(int addr, int num) {
  byte raw[2];
  (int&)raw = num;
  for(byte i = 0; i < 2; i++){
    EEPROM.write(addr+i, raw[i]);
  }
}

void post(int new_request) {
  /*
  {
    "valve": "zk1169",
    "closed": 0,
    "type": 1,
    "new_request": 1,
    "leakage": 0,
    "sensors": [{
      "sensor": "214128",
      "value": "11",
      "last_updated": "2020-03-21 22:42:01",
      "battery": 10,
      "value_exceeded": "",
      "time_exceeded": ""
    }]
  }
  */

  for(int k = 200; k < 206; k++) {
    token_eeprom += char(EEPROM.read(k));
  }

  /* valve */
  doc["valve"] = token_eeprom;
  doc["closed"] = 0;
  doc["type"] = 1;
  doc["new_request"] = new_request;
  doc["leakage"] = 0;

  /* gas sensor */
  sensor["sensor"] = "214128";
  sensor["value"] = "11";
  sensor["last_updated"] = "2020-03-21 22:42:01";
  sensor["battery"] = 10;
  sensor["value_exceeded"] = "";
  sensor["time_exceeded"] = "";

  serializeJson(sensor, sensor_json);

  doc["sensors"] = String('[') + sensor + String(']');
  
  serializeJson(doc, json);

  if ((WiFiMulti.run() == WL_CONNECTED)) {
    Serial.println("ok");
    HTTPClient http;

    if (http.begin("http://40.71.36.211/dashboard/api/update/" + token_eeprom)) {  // HTTPS
      http.POST(json);
      Serial.print(http.getString());
      http.end();
    }
  }
}
