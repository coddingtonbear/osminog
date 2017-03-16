#include "main.h"

#define DHT_11_PIN 10

#define OUTLET_PIN 2
#define OUTLET_ON 5574000
#define OUTLET_OFF 5573952


TinuDHT tinudht;
RCSwitch outletSwitch = RCSwitch();

void setup() {
    Serial.begin(9600);
    outletSwitch.enableTransmit(OUTLET_PIN);
}

void powerOn() {
    outletSwitch.send(OUTLET_ON, 24);
}

void powerOff() {
    outletSwitch.send(OUTLET_OFF, 24);
}


bool updateTemperature() {
    uint8_t tempResult = tinudht_read(&tinudht, DHT_11_PIN);
    if(tempResult == TINUDHT_OK) {
        Serial.println(tinudht.humidity);
        Serial.println(tinudht.temperature);
        return true;
    }

    return false;
}

void loop() {
    if (updateTemperature()) {
        Serial.println(tinudht.humidity);
        Serial.println(tinudht.temperature);
    }
}
