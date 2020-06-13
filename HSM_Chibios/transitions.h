#ifndef TRANSITIONS_H
#define TRANSITIONS_H

#include "event.h"
#include "sm.h"


#define Top_init_tran() do {                    \
                push_state(fn_cb);              \
                dispatch(ENTRY_EVENT);          \
                dispatch(INIT_EVENT);           \
        } while (0)

#define fn_init_tran() do {                     \
                push_state(fn_state1_cb);       \
                dispatch(ENTRY_EVENT);          \
                dispatch(INIT_EVENT);           \
        } while (0)

#define fn_trans1_tran() do {                   \
                push_state(fn_state1_cb);       \
                dispatch(ENTRY_EVENT);          \
        } while (0)

#define fn_state1_init_tran() do {              \
                dispatch(EXIT_EVENT);           \
                replace_state(fn_state2_cb);    \
                dispatch(ENTRY_EVENT);          \
        } while (0)
        
#define fn_state2_tran() do {                   \
                dispatch(EXIT_EVENT);           \
                replace_state(fn_state3_cb);    \
                dispatch(ENTRY_EVENT);          \
        } while (0)
        
#define fn_state3_fn_state2_tran() do {         \
                dispatch(EXIT_EVENT);           \
                replace_state(fn_state2_cb);    \
                dispatch(ENTRY_EVENT);          \
        } while (0)
        
#define fn_state3_fn_state1_tran() do {         \
                dispatch(EXIT_EVENT);           \
                replace_state(fn_state1_cb);    \
                dispatch(ENTRY_EVENT);          \
        } while (0)

#endif /* TRANSITIONS_H */
