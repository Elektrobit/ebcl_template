/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <time.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <getopt.h>

#include "shmlib_proxyshm.h"
#include "shmlib_logger.h"
#include "shmlib_ringbuffer.h"
#include "shmlib_hi_app.h"

#include "common.h"

/**
 * Mode of operation for this application
 */
enum mode {
    MODE_DEFAULT, /**< Default mode, send messages to hi_main and receive results from hi_forward */
    MODE_SUPPRESS_WDG, /**< Send a message to hi_main, to stop triggering the watchdog */
    MODE_PROHIBITED_SYSCALL /**< Send a message to hi_main, to execute a not allowed syscall */
};

struct opts {
    enum mode mode; /**< Selected mode */
    int loops; /**< Number of messages to send in default mode until the application terminates */
} options = {
    .mode = MODE_DEFAULT,
    .loops = 10
};

static struct shmlib_shm_ptr proxyshm;
static struct shmlib_shm shm;
static struct shmlib_hi_app *hi_main, *hi_forward;

static void usage(void)
{
    printf("Usage li_demo [options]\n");
    printf(" with options\n");
    printf("  -l loops  Number of messages to send in default mode\n");
    printf("  -p        Trigger a prohibited syscall in hi_main\n");
    printf("  -s        Trigger suppression of watchdog signal in hi_main\n\n");
}

static void parse_args(int argc, char **argv)
{
    int opt;
    while ((opt = getopt(argc, argv, "l:psh")) != -1) {
        switch (opt) {
        case 'l':
            options.loops = atoi(optarg);
            break;
        case 'p':
            options.mode = MODE_PROHIBITED_SYSCALL;
            break;
        case 's':
            options.mode = MODE_SUPPRESS_WDG;
            break;
        case 'h':
            usage();
            exit(EXIT_SUCCESS);
        default:
            usage();
            exit(EXIT_FAILURE);
        }
    }
}

/**
 * Initialize shared memory, logging and lookup/wait for the high integrity applications
 */
static void init(void)
{
    shmlib_logger_set_min_log_level(SHMLIB_LOGGER_DEBUG);
    shmlib_logger_set_tag("li_demo");

    shmlib_log(SHMLIB_LOGGER_INFO, "Hello from ebclfsa low integrity demo application");

    int ret = shmlib_shm_init(&shm);
    if (ret) {
        shmlib_log_function_failed("shmlib_shm_init", ret);
        exit(EXIT_FAILURE);
    }

    ret = shmlib_shm_get_proxyshm(&shm, &proxyshm);
    if (ret) {
        shmlib_log_function_failed("shmlib_shm_get_proxyshm", ret);
        exit(EXIT_FAILURE);
    }

    shmlib_log(SHMLIB_LOGGER_INFO, "Waiting for high integrity apps to start...");

    /* wait until the high integrity applications are available,
     * because they may still start, when li_demo is executed */
    while (true) {
        static const struct timespec sleep_time = {
            .tv_nsec = 10L * 1000L * 1000L /* 10ms */,
            .tv_sec = 0L,
        };
        shmlib_proxyshm_lock(&proxyshm);
        if (!hi_main) {
            ret = shmlib_proxyshm_find_app(&proxyshm, HI_MAIN_UUID, &hi_main);
        }
        if (!hi_forward) {
            ret = shmlib_proxyshm_find_app(&proxyshm, HI_FORWARD_UUID, &hi_forward);
        }
        shmlib_proxyshm_unlock(&proxyshm);
        if ((hi_main && hi_forward) || ret != -ENOENT) {
            break;
        }
        nanosleep(&sleep_time, NULL);
    }

    if (ret) {
        shmlib_log_function_failed("shmlib_proxyshm_find_app", ret);
    }

    shmlib_log(SHMLIB_LOGGER_INFO, "high integrity apps are available");
}

static void main_loop(void)
{     
    for (int i = 0; i < options.loops; ++i) {
        static const struct timespec sleep_time = {
            .tv_nsec = 0,
            .tv_sec = 1L,
        };
        char buffer[BUFFER_SIZE];
        sprintf(buffer, "Hello hi_app %d", i);
        shmlib_log(SHMLIB_LOGGER_INFO, "Sending '%s'", buffer);
        /* send a message to hi_main */
        int ret = shmlib_ring_buffer_write(&hi_main->li_to_hi, buffer, sizeof(buffer));
        if (ret < 0) {
            shmlib_log_function_failed("shmlib_ring_buffer_write", ret);
            exit(EXIT_FAILURE);
        }
        /* wait for the response from hi_forward */
        while (true) {
            ret = shmlib_ring_buffer_read(&hi_forward->hi_to_li, buffer, sizeof(buffer));
            if (ret > 0) {
                break;
            } else if (ret < 0 && ret != -EAGAIN) {
                shmlib_log_function_failed("shmlib_ring_buffer_read", ret);
                exit(EXIT_FAILURE);
            }
        }
        shmlib_log(SHMLIB_LOGGER_INFO, "Got response: %s", buffer);

        nanosleep(&sleep_time, NULL);
    }
    
}

void send_single_cmd(const char *cmd)
{
    int ret = shmlib_ring_buffer_write(&hi_main->li_to_hi, cmd, strlen(cmd) + 1);
    if (ret < 0) {
        shmlib_log_function_failed("shmlib_ring_buffer_write", ret);
        exit(EXIT_FAILURE);
    }  
}

int main(int argc, char **argv)
{
    parse_args(argc, argv);

    init();

    /* if the mode is not MODE_DEFAULT, sent a command message */
    if (options.mode == MODE_PROHIBITED_SYSCALL) {
        send_single_cmd(CMD_PROHIBITED_SYSCALL);
    } else if (options.mode == MODE_SUPPRESS_WDG) {
        send_single_cmd(CMD_SUPPRESS_WDG);
    } else {
        main_loop();
    }

    return 0; 
}
