/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#define _GNU_SOURCE
#include <time.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <sys/ioctl.h>
#include <sched.h>

#include "shmlib_hi_app.h"
#include "shmlib_logger.h"

#include "common.h"
#include "hi_common.h"

/** Check if hi_forward has triggered its watchdog and if it did, trigger the system watchdog */
static void check_and_signal_watchdog(struct shmlib_watchdog* const watchdog,
                                  struct demo_hicom* const hicom)
{
    uint32_t expected = 1;
    // If the child has set its watchdog bit to 1, set it back to 0 and send heartbeat
    if (__atomic_compare_exchange_n(&hicom->watchdog, &expected, 0, false, __ATOMIC_ACQUIRE,
                                    __ATOMIC_RELAXED)) {
        shmlib_watchdog_do_heartbeat(watchdog);
    }
}

static int start_hi_forward_child(void*)
{
    char* const argv[] = {NULL};
    char* const envp[] = {NULL};
    execve("/hi_forward", argv, envp);
    /* this line should never be reached */
    shmlib_log_function_failed("execve", errno);
    exit(EXIT_FAILURE);
    return 0;
}

static void start_hi_forward(void)
{
    enum {stack_size = 256 * 4096};
    static char stack[stack_size] __attribute__((aligned(4096))) = {0};

    int ret = clone(start_hi_forward_child, stack + stack_size, CLONE_VFORK | CLONE_VM, NULL);
    if (ret == -1) {
        shmlib_log_function_failed("clone", errno);
        exit(EXIT_FAILURE);
    }
}

int main()
{
    struct shmlib_hi_app* app = NULL;
    struct shmlib_shm_ptr watchdog_shm = {0};
    struct shmlib_shm_ptr hicom = {0};
    struct shmlib_watchdog watchdog = {0};
    struct shmlib_shm shm = {0};
    struct demo_hicom *demo_hicom = NULL;
    bool trigger_wdg = true;

    /* Disable buffering, to prevent musl from executing ioctl on print to stdout */
    setbuf(stdout, NULL);

    shmlib_logger_set_min_log_level(SHMLIB_LOGGER_DEBUG);
    shmlib_logger_set_tag("hi_main");

    shmlib_log(SHMLIB_LOGGER_INFO, "Hello from ebclfsa high integrity demo application");

    /* initialize shared memory and register this app in the proxycom */
    int ret = shmlib_hi_app_create_new(&shm, HI_MAIN_UUID, &app, &hicom, &watchdog_shm, true);
    if (ret) {
        shmlib_log_function_failed("shmlib_hi_app_create_new", ret);
        return 1;
    }
    demo_hicom = (struct demo_hicom*) hicom.hicom;
    memset(demo_hicom, 0, sizeof(*demo_hicom));

    start_hi_forward();

    shmlib_watchdog_init(&watchdog, watchdog_shm.watchdog);

    shmlib_log(SHMLIB_LOGGER_INFO, "Entering main loop...");
    while (true) {
        static const struct timespec sleep_time = {
            .tv_nsec = 10L * 1000L * 1000L, /* 10ms */
            .tv_sec = 0L,
        };

        if (trigger_wdg) {
            check_and_signal_watchdog(&watchdog, demo_hicom);
        }

        char buffer_in[BUFFER_SIZE];
        char buffer_out[BUFFER_SIZE];
        /* receive data from li app */
        ret = shmlib_ring_buffer_read(&app->li_to_hi, buffer_in, sizeof(buffer_in));
        if (ret < 0 && ret != -EAGAIN) {
            shmlib_log_function_failed("shmlib_ring_buffer_read", ret);
            return 1;
        } else if (ret > 0) { /* a message was received */
            shmlib_log(SHMLIB_LOGGER_DEBUG, "Received '%s' from li", buffer_in);

            /* check for special command words */
            if (strcmp(buffer_in, CMD_PROHIBITED_SYSCALL) == 0) {
                ioctl(0, 0); /* not allowed syscall */
            } else if (strcmp(buffer_in, CMD_SUPPRESS_WDG) == 0) {
                trigger_wdg = false; /* stop triggering the watchdog */
            } else {
                char *start_of_nr = buffer_in;
                while (!isdigit(*start_of_nr) && *start_of_nr) start_of_nr++;
                snprintf(buffer_out, sizeof(buffer_out), 
                         "You said '%.100s', I say 'hello li_app %d'", buffer_in, atoi(start_of_nr) + 1);
                /* send data to hi_forward*/
                ret = shmlib_ring_buffer_write(&demo_hicom->ring, buffer_out, sizeof(buffer_out));
                if (ret < 0) {
                    shmlib_log_function_failed("shmlib_ring_buffer_write", ret);
                    return 1;
                }
            }
        }

        nanosleep(&sleep_time, NULL);
    }

    return 0; 
}
