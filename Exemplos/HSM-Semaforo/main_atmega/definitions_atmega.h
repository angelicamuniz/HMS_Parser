
// Definição dos pinos de saída
#define SEM1_VERMELHO 4
#define SEM1_AMARELO  3
#define SEM1_VERDE    2

#define SEM2_VERMELHO 5
#define SEM2_AMARELO  6
#define SEM2_VERDE    7

#define SEM3_VERMELHO 8
#define SEM3_VERDE    9


// Definição dos pinos de entrada
#define AMB1      A0
#define AMB2      A1
#define CARRO2    A2
#define PEDESTRE  A3
#define MODO      A4

// Leitura da entrada
#define LEIT_AMB1_PRESENTE        digitalRead(AMB1)
#define LEIT_AMB2_PRESENTE        digitalRead(AMB2)
#define LEIT_CARRO2_PRESENTE      digitalRead(CARRO2)
#define LEIT_PEDESTRE_PRESENTE    digitalRead(PEDESTRE)
#define LEIT_MODO_NOTURNO         digitalRead(MODO)

// Definição de variáveis do código
#define TEMPO_TOUT1     1   //1
#define TEMPO_TOUT5     2   //5
#define TEMPO_TOUT10    4   //10
#define TEMPO_TOUT20    4   //20
#define TEMPO_TOUT30    4   //30

// Funcao para chamar no setup()
//void pins_definitions(){
//  // Saídas
//  pinMode(SEM1_VERMELHO,  OUTPUT);
//  pinMode(SEM1_AMARELO,   OUTPUT);
//  pinMode(SEM1_VERDE,     OUTPUT);
//
//  
//  pinMode(SEM2_VERMELHO,  OUTPUT);
//  pinMode(SEM2_AMARELO,   OUTPUT);
//  pinMode(SEM2_VERDE,     OUTPUT);
//  
//  pinMode(SEM3_VERMELHO,  OUTPUT);
//  pinMode(SEM3_VERDE,     OUTPUT);
//
//  // Entradas
//  pinMode(AMB1,     INPUT);
//  pinMode(AMB2,     INPUT);
//  pinMode(MODO,     INPUT);
//  pinMode(CARRO2,   INPUT);
//  pinMode(PEDESTRE, INPUT);
//}
