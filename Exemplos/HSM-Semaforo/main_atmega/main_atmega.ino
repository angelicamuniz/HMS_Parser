#include "event.h"
#include "guardandactions.h"
#include "hsm.h"
#include "sm.h"
#include "bsp.h"
#include "transitions.h"
#include "definitions_atmega.h"

void verifica_serial()
{
  int char_received;
  char_received = Serial.read();
  if (char_received > -1){
    switch (char_received) {
                
                case 'A':
                case 'a':
                        set_event(EVENT_CARRO2);
                        break;
                case 'B':
                case 'b':
                        set_event(EVENT_AMB1);
                        break;
                case 'C':
                case 'c':
                        set_event(EVENT_TIMEOUT10);
                        break;
                case 'D':
                case 'd':
                        set_event(EVENT_AMB2);
                        break;
                case 'E':
                case 'e':
                        set_event(EVENT_TIMEOUT5);
                        break;
                case 'F':
                case 'f':
                        set_event(EVENT_TIMEOUT20);
                        break;
                case 'G':
                case 'g':
                        set_event(EVENT_TIMEOUT30);
                        break;
                case 'H':
                case 'h':
                        set_event(EVENT_AMB1_LEFT);
                        break;
                case 'I':
                case 'i':
                        set_event(EVENT_TIMEOUT1);
                        break;
                case 'J':
                case 'j':
                        set_event(EVENT_AMB2_LEFT);
                        break;
                case 'K':
                case 'k':
                        set_event(EVENT_PEDESTRE);
                        break;
                case 'L':
                case 'l':
                        set_event(EVENT_TROCA_MODO);
                        break;
                default:
                        set_event(USER_EVENT);
                        /* continue; */
                }
  }
}

void setup() {
  Serial.begin(115200);
  init_machine(init_cb);

  //pins_definitions();

  // Saídas
  pinMode(SEM1_VERMELHO,  OUTPUT);
  pinMode(SEM1_AMARELO,   OUTPUT);
  pinMode(SEM1_VERDE,     OUTPUT);

  
  pinMode(SEM2_VERMELHO,  OUTPUT);
  pinMode(SEM2_AMARELO,   OUTPUT);
  pinMode(SEM2_VERDE,     OUTPUT);
  
  pinMode(SEM3_VERMELHO,  OUTPUT);
  pinMode(SEM3_VERDE,     OUTPUT);

  // Entradas
  pinMode(AMB1,     INPUT);
  pinMode(AMB2,     INPUT);
  pinMode(MODO,     INPUT);
  pinMode(CARRO2,   INPUT);
  pinMode(PEDESTRE, INPUT);
  
}

void loop() {
  event_t ev;
  verifica_serial();
  ev = check_for_events();
  if (ev != 0)
    dispatch_event(ev);
}
