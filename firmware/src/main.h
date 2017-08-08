#include <Arduino.h>
#include <DHT.h>
#include <RCSwitch.h>
#include <Bounce2.h>
#include <SerialCommand.h>

void setup();
void loop();

void powerOn();
void powerOff();
void unrecognized();
void getHumidity();
void getTemperature();
void soundBuzzer();
void soundBuzzer(int milliseconds);
void checkFilament();

bool updateTemperature();
