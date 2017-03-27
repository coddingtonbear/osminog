#include "main.h"

#define DHT_11_PIN 6

#define OUTLET_PIN 5
#define OUTLET_ON 5574000
#define OUTLET_OFF 5573952

#define BUTTON_PIN 3

#define RELAY_PIN 2

#define LED_PIN 16

#define BUZZER_PIN A0


DHT dht(DHT_11_PIN, DHT11);
RCSwitch outletSwitch = RCSwitch();
Bounce button = Bounce();
SerialCommand cmd;

bool poweredOn = false;


void setup() {
    Serial.begin(9600);
    outletSwitch.enableTransmit(OUTLET_PIN);

    dht.begin();

    pinMode(BUTTON_PIN, INPUT_PULLUP);
    button.attach(BUTTON_PIN);
    button.interval(50);

    tone(BUZZER_PIN, 2000, 5000);

    cmd.addCommand("POWEROFF", powerOff);
    cmd.addCommand("POWERON", powerOn);
    cmd.addCommand("GETTEMPERATURE", getTemperature);
    cmd.addCommand("GETHUMIDITY", getHumidity);
    cmd.addDefaultHandler(unrecognized);
    Serial.println("Ready");
}

void unrecognized() {
    Serial.println("Error");
}

void powerOn() {
    outletSwitch.send(OUTLET_ON, 24);
    poweredOn = true;
    Serial.println("Power On Transmitted");
}

void powerOff() {
    outletSwitch.send(OUTLET_OFF, 24);
    poweredOn = false;
    Serial.println("Power Off Transmitted");
}

void getTemperature() {
    Serial.println(dht.readTemperature());
}

void getHumidity() {
    Serial.println(dht.readHumidity());
}


void loop() {
    cmd.readSerial();

    button.update();
    if(button.fell()) {
        if (poweredOn) {
            powerOff();
        } else {
            powerOn();
        }
    }
}
