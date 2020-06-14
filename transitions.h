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
