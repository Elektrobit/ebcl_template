/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <time.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <sys/ioctl.h>

#include "shmlib_hi_app.h"
#include "shmlib_logger.h"

#include "common.h"
#include "hi_common.h"

static void signal_watchdog(struct demo_hicom* const hicom)
{
    __atomic_store_n(&hicom->watchdog, 1, __ATOMIC_RELAXED);
}

int main()
{
    struct shmlib_hi_app* app = NULL;
    struct shmlib_shm_ptr hicom = {0};
    struct shmlib_shm shm = {0};
    struct demo_hicom *demo_hicom = NULL;

    /* Disable buffering, to prevent musl from executing ioctl on print to stdout */
    setbuf(stdout, NULL);

    shmlib_logger_set_min_log_level(SHMLIB_LOGGER_DEBUG);
    shmlib_logger_set_tag("hi_forward");


    shmlib_log(SHMLIB_LOGGER_INFO, "Hello from ebclfsa high integrity demo application");

    /* initialize shared memory and register this app in the proxycom */
    int ret = shmlib_hi_app_create_new(&shm, HI_FORWARD_UUID, &app, &hicom, NULL, false);
    if (ret) {
        shmlib_log_function_failed("shmlib_hi_app_create_new", ret);
        return 1;
    }
    demo_hicom = (struct demo_hicom*) hicom.hicom;

    shmlib_log(SHMLIB_LOGGER_INFO, "Entering main loop...");
    while (true) {
        static const struct timespec sleep_time = {
            .tv_nsec = 10L * 1000L * 1000L, /* 10ms */
            .tv_sec = 0L,
        };

        signal_watchdog(demo_hicom);

        char buffer_in[BUFFER_SIZE];
        char buffer_out[BUFFER_SIZE];
        ret = shmlib_ring_buffer_read(&demo_hicom->ring, buffer_in, sizeof(buffer_in));
        if (ret < 0 && ret != -EAGAIN) {
            shmlib_log_function_failed("shmlib_ring_buffer_read", ret);
            return 1;
        } else if (ret > 0) {
            shmlib_log(SHMLIB_LOGGER_DEBUG, "Received '%s' from hi_demo", buffer_in);

            for (int i = 0; i < BUFFER_SIZE; ++i) {
                buffer_out[i] = toupper(buffer_in[i]);
                if (!buffer_out[i]) {
                    break;
                }
            }

            ret = shmlib_ring_buffer_write(&app->hi_to_li, buffer_out, sizeof(buffer_out));
            if (ret < 0) {
                shmlib_log_function_failed("shmlib_ring_buffer_write", ret);
                return 1;
            }
        }

        nanosleep(&sleep_time, NULL);
    }

    return 0; 
}
