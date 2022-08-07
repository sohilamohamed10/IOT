#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>


// Configure Firebase Variables
#define FIREBASE_HOST  "task1-1a281-default-rtdb.firebaseio.com" 
#define FIREBASE_AUTH "LGe29CPmkWEa7kedlXgIO4iErpcys5zBNylGVE3E" 
#define WIFI_SSID "STUDBME2" 
#define WIFI_PASSWORD "BME2Stud" 

String saved_networks[] = {"","Ashar","Alaa1","STUDBME2","Sohila","Mariooma"};
String scanned_ssids[6];
int rssi_values[6];

int w_len = sizeof(saved_networks)/sizeof(saved_networks[0]);
int s_len = sizeof(scanned_ssids)/sizeof(scanned_ssids[0]);
int s_index = 0;          // index for scanned_ssids
int w_index = 0;          // index for saved_networks
int n = 0;                // number of scanned networks

//String rssi_string;
char rssi_buffer[30];
char* outputStrings[11];
char rssi_characters[30];

void setup() 
{
  Serial.begin(9600);           
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
 
}

void loop()
{   
    Serial.println("WiFi scan started");
  
    // WiFi.scanNetworks will return the number of networks found
    n = WiFi.scanNetworks();

    Serial.println("Wifi scan ended");

    saveValues();
  
    // Displaying the scanned WiFis
    if (n == 0)
    {
        Serial.println("no networks found");
    }
    else
    {
        printToSerial();
        convertIntToString();
          Firebase.pushString("/RSSI", rssi_characters);            
    if (Firebase.failed()) 
    {
 
      Serial.print("pushing /logs failed:");
      Serial.println(Firebase.error()); 
      return;
  }
        // Reset rssi_characters
        memset(rssi_characters, 0, 30);
        
    }
    Serial.println("");
  
    // Wait a bit before scanning again
    delay(1000);
    WiFi.scanDelete();      
}

void saveValues()
{
  // Save SSIDs and RSSIs to array
    for (int i = 0; i < n; ++i)
    {
        // Check if the ssid exists in the saved networks
        s_index = findElement(saved_networks, w_len, WiFi.SSID(i));
        if (s_index != -1)
        {
            scanned_ssids[s_index] = WiFi.SSID(i);
            rssi_values[s_index] = WiFi.RSSI(i);
        }
    }

    // Check if there's a network in saved and not scanned (Error while scanning)
    // So put it's RSSI = 0 (Take average later)
    for (int i = 0; i < w_len; i++)
    {
        w_index = findElement(scanned_ssids, w_len, saved_networks[i]);
        // If it is saved network and not scanned -> put rssi = 0
        if (w_index == -1)
        {
            scanned_ssids[i] = saved_networks[i];
            rssi_values[i] = 0;
        }
    }
}


void printToSerial()
{
  Serial.print(n);
  Serial.println(" networks found");
        
  for (int i = 0; i < s_len; ++i)
  {
      // Print SSID and RSSI for each network found
      Serial.print("(");
      Serial.print(i + 1);
      Serial.print(") ");
      Serial.print(scanned_ssids[i]);       // SSID
      Serial.print("  ");
                              
      Serial.print(rssi_values[i]);       //Signal strength in dBm  
      Serial.println(" dBm");

      delay(20);
  }  
}

void convertIntToString()
{
    // Convert array of int to string -> to sent to firebase with setString
    for (int i = 0 ; i < w_len ; ++i)
    {
        snprintf(rssi_buffer, 30, "%d ", rssi_values[i]);
        // check for overrun omitted
        outputStrings[i] = strdup(rssi_buffer);
        strcat(rssi_characters, outputStrings[i]);
    }  
}

// Function to find element in an array
// return its index if found and -1 if not
int findElement(String arr[], int n, String val)
{
    int indx = -1;

    for (int i = 0; i < n; i++)
    {
        // if found -> 0 -> !0 = 1 = True
        if(val == String(arr[i]))
        {
            indx = i;
            break;
        }
    }
    return indx;
}