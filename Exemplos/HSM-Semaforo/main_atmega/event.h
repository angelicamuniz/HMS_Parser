#ifndef EVENTS_H
#define EVENTS_H

#include <stdint.h>

typedef uint32_t event_t;

#if defined(__cplusplus)
extern "C"
{
#endif
event_t wait_for_events(void);
event_t check_for_events(void);
event_t test_for_event(event_t);
#if defined(__cplusplus)
}
#endif

extern volatile event_t _events;
#define set_event(ev)                           \
        do {                                    \
                enter_critical_region();        \
                _events |= (1 << (ev));         \
                leave_critical_region();        \
        } while (0)

#define MAX_EVENTS 32

enum {
    EVENT0 = 0,
    EVENT1,
    EVENT2,
    EVENT3,
    EVENT4,
    EVENT5,
    EVENT6,
    EVENT7,
    EVENT8,
    EVENT9,
    EVENT10,
    EVENT11,
    EVENT12,
    EVENT13,
    EVENT14,
    EVENT15,
    EVENT16,
    EVENT17,
    EVENT18,
    EVENT19,
    EVENT20,
    EVENT21,
    EVENT22,
    EVENT23,
    EVENT24,
    EVENT25,
    EVENT26,
    EVENT27,
    EVENT28,
    EVENT29,
    EVENT30,
    EVENT31
};

#endif /* EVENTS_H */
