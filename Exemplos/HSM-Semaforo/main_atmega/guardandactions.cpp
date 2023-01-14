#include "guardandactions.h"
#include "definitions_atmega.h"
#include <stdio.h>
#include <Arduino.h>
#include <avr/pgmspace.h>

extern char buffer[100];


/* Guard Conditions: */
int carro2_presente()
{
    const static char PROGMEM gc_msg[] = "GC: carro2_presente()";
    strcpy_P(buffer, (char *) gc_msg);
	Serial.println(buffer);
    /* Desenvolva aqui sua funcao.*/
    return LEIT_CARRO2_PRESENTE;
}


int pedestre_presente()
{
    const static char PROGMEM gc_msg[] = "GC: pedestre_presente()";
    strcpy_P(buffer, (char *) gc_msg);
	Serial.println(buffer);
    /* Desenvolva aqui sua funcao.*/
    return LEIT_PEDESTRE_PRESENTE;
}


int amb1_presente()
{
    const static char PROGMEM gc_msg[] = "GC: amb1_presente()";
    strcpy_P(buffer, (char *) gc_msg);
	Serial.println(buffer);
    /* Desenvolva aqui sua funcao.*/
    return LEIT_AMB1_PRESENTE;
}


int amb2_presente()
{
    const static char PROGMEM gc_msg[] = "GC: amb2_presente()";
    strcpy_P(buffer, (char *) gc_msg);
	Serial.println(buffer);
    /* Desenvolva aqui sua funcao.*/
    return LEIT_AMB2_PRESENTE;
}



/* Actions: */
int acende_amarelo2()
{
    const static char PROGMEM action_msg[] = "ACTION: acende_amarelo2()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
    digitalWrite(SEM1_VERMELHO, HIGH);
    digitalWrite(SEM1_AMARELO, LOW);
    digitalWrite(SEM1_VERDE, LOW);
    digitalWrite(SEM2_VERMELHO, LOW);
    digitalWrite(SEM2_AMARELO, HIGH);
    digitalWrite(SEM2_VERDE, LOW);
    digitalWrite(SEM3_VERMELHO, HIGH);
    digitalWrite(SEM3_VERDE, LOW);
    return 1;
}


int apaga_verde3()
{
    const static char PROGMEM action_msg[] = "ACTION: apaga_verde3()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, HIGH);
  digitalWrite(SEM1_AMARELO, LOW);
  digitalWrite(SEM1_VERDE, LOW);
  digitalWrite(SEM2_VERMELHO, HIGH);
  digitalWrite(SEM2_AMARELO, LOW);
  digitalWrite(SEM2_VERDE, LOW);
  digitalWrite(SEM3_VERMELHO, LOW);
  digitalWrite(SEM3_VERDE, LOW);
    return 1;
}


int acende_verde3()
{
    const static char PROGMEM action_msg[] = "ACTION: acende_verde3()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, HIGH);
  digitalWrite(SEM1_AMARELO, LOW);
  digitalWrite(SEM1_VERDE, LOW);
  digitalWrite(SEM2_VERMELHO, HIGH);
  digitalWrite(SEM2_AMARELO, LOW);
  digitalWrite(SEM2_VERDE, LOW);
  digitalWrite(SEM3_VERMELHO, LOW);
  digitalWrite(SEM3_VERDE, HIGH);
    return 1;
}


int apaga_amarelos_not()
{
    const static char PROGMEM action_msg[] = "ACTION: apaga_amarelos_not()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, LOW);
  digitalWrite(SEM1_AMARELO, LOW);
  digitalWrite(SEM1_VERDE, LOW);
  digitalWrite(SEM2_VERMELHO, LOW);
  digitalWrite(SEM2_AMARELO, LOW);
  digitalWrite(SEM2_VERDE, LOW);
  digitalWrite(SEM3_VERMELHO, LOW);
  digitalWrite(SEM3_VERDE, LOW);
    return 1;
}


int acende_amarelo1()
{
    const static char PROGMEM action_msg[] = "ACTION: acende_amarelo1()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, LOW);
  digitalWrite(SEM1_AMARELO, HIGH);
  digitalWrite(SEM1_VERDE, LOW);
  digitalWrite(SEM2_VERMELHO, HIGH);
  digitalWrite(SEM2_AMARELO, LOW);
  digitalWrite(SEM2_VERDE, LOW);
  digitalWrite(SEM3_VERMELHO, HIGH);
  digitalWrite(SEM3_VERDE, LOW);
    return 1;
}


int acende_amarelos_not()
{
    const static char PROGMEM action_msg[] = "ACTION: acende_amarelos_not()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, LOW);
  digitalWrite(SEM1_AMARELO, HIGH);
  digitalWrite(SEM1_VERDE, LOW);
  digitalWrite(SEM2_VERMELHO, LOW);
  digitalWrite(SEM2_AMARELO, HIGH);
  digitalWrite(SEM2_VERDE, LOW);
  digitalWrite(SEM3_VERMELHO, LOW);
  digitalWrite(SEM3_VERDE, LOW);
    return 1;
}


int acende_verde1()
{
    const static char PROGMEM action_msg[] = "ACTION: acende_verde1()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, LOW);
  digitalWrite(SEM1_AMARELO, LOW);
  digitalWrite(SEM1_VERDE, HIGH);
  digitalWrite(SEM2_VERMELHO, HIGH);
  digitalWrite(SEM2_AMARELO, LOW);
  digitalWrite(SEM2_VERDE, LOW);
  digitalWrite(SEM3_VERMELHO, HIGH);
  digitalWrite(SEM3_VERDE, LOW);
    return 1;
}


int acende_verde2()
{
    const static char PROGMEM action_msg[] = "ACTION: acende_verde2()";
    strcpy_P(buffer, (char *) action_msg);
	Serial.println(buffer);
	/* Desenvolva aqui sua funcao.*/
  digitalWrite(SEM1_VERMELHO, HIGH);
  digitalWrite(SEM1_AMARELO, LOW);
  digitalWrite(SEM1_VERDE, LOW);
  digitalWrite(SEM2_VERMELHO, LOW);
  digitalWrite(SEM2_AMARELO, LOW);
  digitalWrite(SEM2_VERDE, HIGH);
  digitalWrite(SEM3_VERMELHO, HIGH);
  digitalWrite(SEM3_VERDE, LOW);
    return 1;
}
