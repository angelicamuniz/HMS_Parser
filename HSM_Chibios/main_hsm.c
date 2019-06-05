#include <avr/pgmspace.h>
#include "ch.h"
#include "hal.h"
#include "chprintf.h"
#include "event.h"
#include "sm.h"
#include "transitions.h"
#include <string.h>

enum {
        EVENT_EV1 = USER_EVENT,
        EVENT_EV2,
        EVENT_EV3,
	EVENT_TIMEOUT
};


/*
 * Funções de callback de cada estado. É assim que se define um estado.
 * Transições de acordo com o evento recebido.
 * A transição é realizada a partir de uma função como: s11_s_local_tran();
 * E cada callback retorna sempre se o evento foi tratado ou não: EVENT_HANDLED ou EVENT_NOT_HANDLED
 * Objetivo de informar se foi tratado ou não.
 */

cb_status fn_cb(event_t ev);

cb_status fn_state1_cb(event_t ev);
cb_status fn_state2_cb(event_t ev);
cb_status fn_state3_cb(event_t ev);

virtual_timer_t vt_timeout;

void cb_timeout (void*arg)
{
    set_event(EVENT_TIMEOUT);  
}

cb_status init_cb(event_t ev)
{
        Top_init_tran();
        return EVENT_HANDLED;
}

cb_status fn_cb(event_t ev)
{
        switch(ev) {
        case ENTRY_EVENT:
                return EVENT_HANDLED;
        case EXIT_EVENT:
                return EVENT_HANDLED;
        case INIT_EVENT:
                fn_init_tran();
                return EVENT_HANDLED;
        case EVENT_EV1:
                fn_trans1_tran();
                return EVENT_HANDLED;
        case EVENT_EV2:
                return EVENT_HANDLED;
        case EVENT_EV3:
                return EVENT_HANDLED;
        }

        return EVENT_NOT_HANDLED;
}

cb_status fn_state1_cb(event_t ev)
{
        switch(ev) {
        case ENTRY_EVENT:
                return EVENT_HANDLED;
        case EXIT_EVENT:
                return EVENT_HANDLED;
        case INIT_EVENT:
                fn_state1_init_tran();
                return EVENT_HANDLED;
        }

        return EVENT_NOT_HANDLED;
}

cb_status fn_state2_cb(event_t ev)
{
        switch(ev) {
        case ENTRY_EVENT:
                return EVENT_HANDLED;
        case EXIT_EVENT:
                return EVENT_HANDLED;
        case EVENT_TIMEOUT1:
                fn_state2_tran();
                return EVENT_HANDLED;
        }
        return EVENT_NOT_HANDLED;
}

cb_status fn_state3_cb(event_t ev)
{
        switch(ev) {
        case ENTRY_EVENT:
                return EVENT_HANDLED;
        case EXIT_EVENT:
                if (  ) {
                    set_event(EVENT_EV1);
                } else if ( ) {
                    set_event(EVENT_EV2);
                }
                return EVENT_HANDLED;
        case EVENT_EV1:
                fn_state3_fn_state2_tran();
                return EVENT_HANDLED;
        case EVENT_EV2:
                fn_state3_fn_state1_tran();
                return EVENT_HANDLED;
        case EVENT_EV3:
                return EVENT_HANDLED;
        }

        return EVENT_NOT_HANDLED;
}

static THD_WORKING_AREA(waThread1, 32);
static THD_FUNCTION(Thread1, arg) {

  (void)arg;
  chRegSetThreadName("Thread1");
  sdStart(&SD1, 0);
  while(1) {
        *ptr = sdGet(&SD1);
        switch (*ptr) {
                case 'A':
                case 'a':
                        set_event(EVENT_EV1);
                        break;
                case 'B':
                case 'b':
                        set_event(EVENT_EV2);
                        break;
                case 'C':
                case 'c':
                        set_event(EVENT_EV3);
                        break;
                        /* continue; */
            }
      }
}


int main(int argc, char* argv[])
{
    
    
    halInit();
    chSysInit();

    sdStart(&SD1, 0);
    
    palSetGroupMode(IOPORT2, 0x03, 0, PAL_MODE_OUTPUT_PUSHPULL);
    palSetGroupMode(IOPORT3, 0x3F, 0, PAL_MODE_OUTPUT_PUSHPULL);
    palWritePort(IOPORT2, 0);
    palWritePort(IOPORT3, 0);
    
    chVTObjectInit(&vt_timeout1);
    chVTObjectInit(&vt_timeout2);

    init_machine(init_cb);

    chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO + 1, Thread1, NULL);
    
    while (true) {
        dispatch_event(wait_for_events());
    }
    
    return 0;
}
