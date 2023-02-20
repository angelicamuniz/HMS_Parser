#include "event.h"
#include "sm.h"
#include "transitions.h"
#include "guardandactions.h"
#include "bsp.h"
#include "hsm.h"
#include <stdio.h>
#include <Arduino.h>
#include <avr/pgmspace.h>
#include <TimerOne.h>
#include "definitions_atmega.h"

int cont1 = 0;
int cont5 = 0;
int cont10 = 0;
int cont20 = 0;
int cont30 = 0;
int cont_ped = 0;
bool modnot = false;

void set_TEMPO_TOUT1(){
  cont1++;
  cont_ped++;
  if (cont1 > TEMPO_TOUT1) {
    Timer1.detachInterrupt();
    set_event(EVENT_TIMEOUT1);
    cont1 = 0;
  }
  if (cont_ped > 12*TEMPO_TOUT1){
    set_event(EVENT_TIMEOUT10);
    cont_ped = 0;
  }
}

void set_TEMPO_TOUT10(){
  cont10++;
  if (cont10 > TEMPO_TOUT10) {
    Timer1.detachInterrupt();
    set_event(EVENT_TIMEOUT10);
    cont10 = 0;
  }
}

void set_TEMPO_TOUT5(){
  cont5++;
  if (cont5 > TEMPO_TOUT5) {
    Timer1.detachInterrupt();
    set_event(EVENT_TIMEOUT5);
    cont5 = 0;
  }
}

void set_TEMPO_TOUT20(){
  cont20++;
  if (cont20 > TEMPO_TOUT20) {
    Timer1.detachInterrupt();
    set_event(EVENT_TIMEOUT20);
    cont20 = 0;
  }
}

void set_TEMPO_TOUT30(){
  cont30++;
  if (cont30 > TEMPO_TOUT30) {
    Timer1.detachInterrupt();
    set_event(EVENT_TIMEOUT30);
    cont30 = 0;
  }
}



char buffer[100];

cb_status init_cb(event_t ev)
{
  top_init_tran();
  return EVENT_HANDLED;
}

cb_status fn_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      if (LEIT_MODO_NOTURNO)
        set_event(EVENT_TROCA_MODO);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case INIT_EVENT:
      const static char PROGMEM init_msg[] = "INIT_EVENT..fn";
      strcpy_P(buffer, (char *) init_msg);
      Serial.println(buffer);
      fn_init_fn_sem1_tran();
      return EVENT_HANDLED;
    case EVENT_TROCA_MODO:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TROCA_MODO";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (LEIT_MODO_NOTURNO)
        fn_modonot_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem1_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem1";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem1";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      acende_verde1();
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case INIT_EVENT:
      const static char PROGMEM init_msg[] = "INIT_EVENT..fn_sem1";
      strcpy_P(buffer, (char *) init_msg);
      Serial.println(buffer);
      acende_verde1();
      fn_sem1_init_fn_sem1_verde1_tran();
      return EVENT_HANDLED;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem1_verde1_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem1_verde1";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem1_verde1";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(1000000);
      Timer1.attachInterrupt(set_TEMPO_TOUT10);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT10:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT10";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (amb1_presente()) {
        fn_sem1_verde1_fn_sem1_verde_amb1_tran();
        return EVENT_HANDLED;
      } else if (amb2_presente()) {
        acende_amarelo1();
        fn_sem1_verde1_fn_sem1_amarelo_tran();
        return EVENT_HANDLED;
      } else fn_sem1_verde1_fn_sem1_verde2_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem1_verde2_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem1_verde2";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem1_verde2";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT30);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_AMB1:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_AMB1";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      fn_sem1_verde2_fn_sem1_verde_amb1_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_AMB2:
      const static char PROGMEM event_msg1[] = "EVENT..EVENT_AMB2";
      strcpy_P(buffer, (char *) event_msg1);
      Serial.println(buffer);
      acende_amarelo1();
      fn_sem1_verde2_fn_sem1_amarelo_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_TIMEOUT30:
      const static char PROGMEM event_msg2[] = "EVENT..EVENT_TIMEOUT30";
      strcpy_P(buffer, (char *) event_msg2);
      Serial.println(buffer);
      if (carro2_presente()) {
        acende_amarelo1();
        fn_sem1_verde2_fn_sem1_amarelo_tran();
        return EVENT_HANDLED;
      } else if (pedestre_presente()) {
        acende_amarelo1();
        fn_sem1_verde2_fn_sem1_amarelo_tran();
        return EVENT_HANDLED;
      } else fn_sem1_verde2_fn_sem1_verde3_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem1_verde3_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem1_verde3";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem1_verde3";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_AMB1:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_AMB1";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      fn_sem1_verde3_fn_sem1_verde_amb1_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_AMB2:
      const static char PROGMEM event_msg1[] = "EVENT..EVENT_AMB2";
      strcpy_P(buffer, (char *) event_msg1);
      Serial.println(buffer);
      acende_amarelo1();
      fn_sem1_verde3_fn_sem1_amarelo_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_PEDESTRE:
      const static char PROGMEM event_msg2[] = "EVENT..EVENT_PEDESTRE";
      strcpy_P(buffer, (char *) event_msg2);
      Serial.println(buffer);
      acende_amarelo1();
      fn_sem1_verde3_fn_sem1_amarelo_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_CARRO2:
      const static char PROGMEM event_msg3[] = "EVENT..EVENT_CARRO2";
      strcpy_P(buffer, (char *) event_msg3);
      Serial.println(buffer);
      acende_amarelo1();
      fn_sem1_verde3_fn_sem1_amarelo_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem1_verde_amb1_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem1_verde_amb1";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem1_verde_amb1";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_AMB1_LEFT:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_AMB1_LEFT";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (amb2_presente()) {
        acende_amarelo1();
        fn_sem1_verde_amb1_fn_sem1_amarelo_tran();
        return EVENT_HANDLED;
      } else if (carro2_presente()) {
        acende_amarelo1();
        fn_sem1_verde_amb1_fn_sem1_amarelo_tran();
        return EVENT_HANDLED;
      } else if (pedestre_presente()) {
        acende_amarelo1();
        fn_sem1_verde_amb1_fn_sem1_amarelo_tran();
        return EVENT_HANDLED;
      } else fn_sem1_verde_amb1_fn_sem1_verde3_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem1_amarelo_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem1_amarelo";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem1_amarelo";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT5);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT5:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT5";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (amb2_presente()) {
        acende_verde2();
        fn_sem1_amarelo_fn_sem2_verde_amb2_tran();
        return EVENT_HANDLED;
      } else if (carro2_presente()) {
        acende_verde2();
        fn_sem1_amarelo_fn_sem2_tran();
        return EVENT_HANDLED;
      } else if (pedestre_presente()) {
        acende_verde3();
        fn_sem1_amarelo_fn_sem3_tran();
        return EVENT_HANDLED;
      } else acende_verde2();
      fn_sem1_amarelo_fn_sem2_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem2_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem2";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem2";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case INIT_EVENT:
      const static char PROGMEM init_msg[] = "INIT_EVENT..fn_sem2";
      strcpy_P(buffer, (char *) init_msg);
      Serial.println(buffer);
      acende_verde2();
      fn_sem2_init_fn_sem2_verde1_tran();
      return EVENT_HANDLED;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem2_verde1_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem2_verde1";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem2_verde1";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(1000000);
      Timer1.attachInterrupt(set_TEMPO_TOUT10);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT10:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT10";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (amb2_presente()) {
        fn_sem2_verde1_fn_sem2_verde_amb2_tran();
        return EVENT_HANDLED;
      } else fn_sem2_verde1_fn_sem2_verde2_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem2_verde2_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem2_verde2";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem2_verde2";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT30);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_AMB2:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_AMB2";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      fn_sem2_verde2_fn_sem2_verde_amb2_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_AMB1:
      const static char PROGMEM event_msg1[] = "EVENT..EVENT_AMB1";
      strcpy_P(buffer, (char *) event_msg1);
      Serial.println(buffer);
      acende_amarelo2();
      fn_sem2_verde2_fn_sem2_amarelo_tran();
      return EVENT_HANDLED;
      break;
    case EVENT_TIMEOUT30:
      const static char PROGMEM event_msg2[] = "EVENT..EVENT_TIMEOUT30";
      strcpy_P(buffer, (char *) event_msg2);
      Serial.println(buffer);
      acende_amarelo2();
      fn_sem2_verde2_fn_sem2_amarelo_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem2_verde_amb2_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem2_verde_amb2";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem2_verde_amb2";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      acende_verde2();
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_AMB2_LEFT:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_AMB2_LEFT";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      fn_sem2_verde_amb2_fn_sem2_verde2_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem2_amarelo_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem2_amarelo";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem2_amarelo";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT5);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT5:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT5";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (amb2_presente()) {
        acende_verde1();
        fn_sem2_amarelo_fn_sem1_verde_amb1_tran();
        return EVENT_HANDLED;
      } else acende_verde1();
      fn_sem2_amarelo_fn_sem1_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem3_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem3";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem3";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case INIT_EVENT:
      const static char PROGMEM init_msg[] = "INIT_EVENT..fn_sem3";
      strcpy_P(buffer, (char *) init_msg);
      Serial.println(buffer);
      acende_verde3();
      fn_sem3_init_fn_sem3_verde_tran();
      return EVENT_HANDLED;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem3_verde_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem3_verde";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem3_verde";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT20);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT20:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT20";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      fn_sem3_verde_fn_sem3_pisca_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem3_pisca_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem3_pisca";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem3_pisca";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
//      Timer1.initialize(1000000);
//      Timer1.attachInterrupt(set_TEMPO_TOUT10);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case INIT_EVENT:
      const static char PROGMEM init_msg[] = "INIT_EVENT..fn_sem3_pisca";
      strcpy_P(buffer, (char *) init_msg);
      Serial.println(buffer);
      fn_sem3_pisca_init_fn_sem3_pisca_on_tran();
      return EVENT_HANDLED;
    case EVENT_TIMEOUT10:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT10";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      apaga_verde3();
      if (amb1_presente()) {
        fn_sem3_pisca_fn_sem1_verde_amb1_tran();
        return EVENT_HANDLED;
      } else if (amb2_presente()) {
        fn_sem3_pisca_fn_sem2_verde_amb2_tran();
        return EVENT_HANDLED;
      } else if (carro2_presente()) {
        fn_sem3_pisca_fn_sem2_tran();
        return EVENT_HANDLED;
      } else fn_sem3_pisca_fn_sem1_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem3_pisca_on_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem3_pisca_on";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem3_pisca_on";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT1);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT1:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT1";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      apaga_verde3();
      fn_sem3_pisca_on_fn_sem3_pisca_off_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status fn_sem3_pisca_off_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..fn_sem3_pisca_off";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..fn_sem3_pisca_off";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT1);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT1:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT1";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      acende_vermelho3();
      fn_sem3_pisca_off_fn_sem3_pisca_on_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status modonot_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..modonot";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..modonot";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case INIT_EVENT:
      const static char PROGMEM init_msg[] = "INIT_EVENT..modonot";
      strcpy_P(buffer, (char *) init_msg);
      Serial.println(buffer);
      acende_amarelos_not();
      modonot_init_modonot_amarelos_on_tran();
      return EVENT_HANDLED;
    case EVENT_TROCA_MODO:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TROCA_MODO";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      if (!LEIT_MODO_NOTURNO)
        modonot_fn_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status modonot_amarelos_on_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..modonot_amarelos_on";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..modonot_amarelos_on";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT1);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT1:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT1";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      apaga_amarelos_not();
      modonot_amarelos_on_modonot_amarelos_off_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}

cb_status modonot_amarelos_off_cb(event_t ev)
{
  const static char PROGMEM entry_msg[] = "ENTRY_EVENT..modonot_amarelos_off";
  const static char PROGMEM exit_msg[] = "EXIT_EVENT..modonot_amarelos_off";
  switch (ev) {
    case ENTRY_EVENT:
      strcpy_P(buffer, (char *) entry_msg);
      Serial.println(buffer);
      Timer1.initialize(500000);
      Timer1.attachInterrupt(set_TEMPO_TOUT1);
      return EVENT_HANDLED;
    case EXIT_EVENT:
      strcpy_P(buffer, (char *) exit_msg);
      Serial.println(buffer);
      return EVENT_HANDLED;
    case EVENT_TIMEOUT1:
      const static char PROGMEM event_msg[] = "EVENT..EVENT_TIMEOUT1";
      strcpy_P(buffer, (char *) event_msg);
      Serial.println(buffer);
      acende_amarelos_not();
      modonot_amarelos_off_modonot_amarelos_on_tran();
      return EVENT_HANDLED;
      break;
  }
  return EVENT_NOT_HANDLED;
}
