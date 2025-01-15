/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_WATCHDOG_H
#define SHMLIB_WATCHDOG_H

#include <stdbool.h>
#include <stdint.h>

/**
 * @brief A shared memory buffer used for communication with the watchdog.
 */
typedef uint8_t* shmlib_wd_t;

struct shmlib_watchdog {
    bool enabled;
    shmlib_wd_t mapping;
};

/**
 * @brief Initialise the given watchdog struct.
 *
 * @param watchdog Watchdog struct to initialise.
 * @param mapping Memory address of the watchdog shared memory.
 */
void shmlib_watchdog_init(struct shmlib_watchdog* watchdog, shmlib_wd_t mapping);

/**
 * @brief Feed the watchdog by performing a heartbeat.
 *
 * @param watchdog Watchdog to feed.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EBUSY if the watchdog is not enabled.
 */
int shmlib_watchdog_do_heartbeat(struct shmlib_watchdog* watchdog);

/**
 * @brief Check if the watchdog has been initialised on the monitoring side.
 *
 * @param watchdog Watchdog to check.
 */
bool shmlib_watchdog_is_alive_check(struct shmlib_watchdog* watchdog);

#endif /* SHMLIB_WATCHDOG_H */
