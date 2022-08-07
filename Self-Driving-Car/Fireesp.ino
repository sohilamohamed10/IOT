#include <ArduinoJson.h>


#include <Firebase.h>
#include <FirebaseArduino.h>
#include <FirebaseCloudMessaging.h>
#include <FirebaseError.h>
#include <FirebaseHttpClient.h>
#include <FirebaseObject.h>

#include <ESP8266WiFi.h>  
#include <string.h>               
#include <FirebaseArduino.h>        
#define FIREBASE_HOST  "rccar-2a976-default-rtdb.firebaseio.com" 
#define FIREBASE_AUTH "nbjt9Caw5d2RpjQcf4kFArcO0FDKnW13k00HLBCs"         
#define WIFI_SSID "STUDBME2"                                  
#define WIFI_PASSWORD "BME2Stud"            

int n;  
int Data1=0;
int Data2=0;
//String n;
 
void setup() 

{
  Serial.begin(115200);
            
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);                                  
  Serial.print("Connecting to ");
  Serial.print(WIFI_SSID);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
 
  Serial.println();
  Serial.print("Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());                               //prints local IP address
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);                 // connect to the firebase
  pinMode(D1,OUTPUT);  
  pinMode(D2,OUTPUT); 
  
 
}
 
void loop() 
{
//  n=1;
// delay(500);
 n=Firebase.getInt("dir_auto");
//  Serial.print(n);
 
 if (n==2) {  
      Serial.println("left");  
      digitalWrite(D1,0); 
      digitalWrite(D2,1);  
  }  
   else if (n==1){  
   Serial.println("right");  
   digitalWrite(D1,1); 
    digitalWrite(D2,0); 
 }

 
 else if (n==3){  
  Serial.println("straight");  
   digitalWrite(D1,1); 
   digitalWrite(D2,1); 
 } 
 else if(n==0){  
  Serial.println("stop");  
  digitalWrite(D1,0); 
   digitalWrite(D2,0); 
//   Serial.println(D1); 
//   Serial.println(D2); 
 } 
   Data1=digitalRead(D1); 
   Data2=digitalRead(D2); 
   Serial.println(Data1);
   Serial.println(Data2);

  delay(100);

}
