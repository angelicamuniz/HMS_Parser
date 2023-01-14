#ifndef HSM_H
#define HSM_H

#include "sm.h"
#include "event.h"
enum {
    EVENT_CARRO2 = USER_EVENT,
    EVENT_AMB1,
    EVENT_TIMEOUT10,
    EVENT_AMB2,
    EVENT_TIMEOUT5,
    EVENT_TIMEOUT20,
    EVENT_TIMEOUT30,
    EVENT_AMB1_LEFT,
    EVENT_TIMEOUT1,
    EVENT_AMB2_LEFT,
    EVENT_PEDESTRE,
    EVENT_TROCA_MODO,
};


#if defined(__cplusplus)
extern "C"
{
#endif
cb_status init_cb(event_t ev);
cb_status fn_cb(event_t ev);
cb_status fn_sem1_cb(event_t ev);
cb_status fn_sem1_verde1_cb(event_t ev);
cb_status fn_sem1_verde2_cb(event_t ev);
cb_status fn_sem1_verde3_cb(event_t ev);
cb_status fn_sem1_verde_amb1_cb(event_t ev);
cb_status fn_sem1_amarelo_cb(event_t ev);
cb_status fn_sem2_cb(event_t ev);
cb_status fn_sem2_verde1_cb(event_t ev);
cb_status fn_sem2_verde2_cb(event_t ev);
cb_status fn_sem2_verde_amb2_cb(event_t ev);
cb_status fn_sem2_amarelo_cb(event_t ev);
cb_status fn_sem3_cb(event_t ev);
cb_status fn_sem3_verde_cb(event_t ev);
cb_status fn_sem3_pisca_cb(event_t ev);
cb_status fn_sem3_pisca_on_cb(event_t ev);
cb_status fn_sem3_pisca_off_cb(event_t ev);
cb_status modonot_cb(event_t ev);
cb_status modonot_amarelos_on_cb(event_t ev);
cb_status modonot_amarelos_off_cb(event_t ev);

#if defined(__cplusplus)
}
#endif

#endif