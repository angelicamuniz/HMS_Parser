#ifndef TRANSITIONS_H
#define TRANSITIONS_H

#include "event.h"
#include "sm.h"

                                  
/*
 * É mais eficiente criar as funções como uma MACRO.
 * Para implementar uma função com mais de uma linha, por padrão C deve ser criada a partir de um do {} while() 
 * porque é como se fosse uma única instrução que dentro tem um conjunto de instruções.
 */

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
