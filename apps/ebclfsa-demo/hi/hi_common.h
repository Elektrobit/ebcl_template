#include <stdint.h>

#include "shmlib_ringbuffer.h"

/**
 * Communication between high integrity applications
 */
struct demo_hicom
{
    /**
     * Watchdog signal from hi_forward to hi_main.
     * hi_forward will set this to 1 and hi_main resets it to zero.
     */
    uint32_t watchdog;
    /**
     * Ring buffer for sending messages from hi_main to hi_forward
     */
    struct shmlib_ring_buffer ring;
};
