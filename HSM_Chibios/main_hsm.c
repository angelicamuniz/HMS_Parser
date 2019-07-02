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


cb_status fn_cb(event_t ev);

cb_status fn_state1_cb(event_t ev);
cb_status fn_state2_cb(event_t ev);
cb_status fn_state3_cb(event_t ev);

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



int main(int argc, char* argv[])
{
    init_machine(init_cb);

    while (true) {
        dispatch_event(wait_for_events());
    }
    
    return 0;
}
