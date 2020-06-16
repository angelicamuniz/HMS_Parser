#ifndef TRANSITIONS_H
#define TRANSITIONS_H

#include "event.h"
#include "sm.h"

cb_status fn_S2_cb(event_t ev);
cb_status fn_S21_cb(event_t ev);
cb_status fn_S22_cb(event_t ev);
cb_status fn_S3_cb(event_t ev);

#define Top_init_tran() do {                    
        } while (0)

#define __tran() do {                    \
                exit_inner_states();            \
                push_state(s1_cb);              \
                dispatch(ENTRY_EVENT);          \
                push_state(s11_cb);             \
                dispatch(ENTRY_EVENT);          \
        } while (0)
