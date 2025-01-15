/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#include "shmlib_watchdog.h"

/**
 * @brief Register offsets inside the watchdog shared memory.
 */
enum shmlib_watchdog_offset {
    SHMLIB_WDG_REG_CTRL = 0x00,
    SHMLIB_WDG_REG_COUNTER_LO = 0x08,
    SHMLIB_WDG_REG_COUNTER_HI = 0x0c,
    SHMLIB_WDG_CTRL_RUNNING = 1U << 0U
};


static inline uint32_t* watchdog_ptr(const struct shmlib_watchdog* const watchdog,
                                            unsigned const offset)
{
    if (!watchdog) {
        return NULL;
    }

    return (uint32_t*)((uint8_t*)watchdog->mapping + offset);
}

static int read32(const struct shmlib_watchdog* const watchdog, const unsigned offset,
                           uint32_t* const dest)
{
    uint32_t* ptr = NULL;
    if (!watchdog || !dest) {
        return -EINVAL;
    }

    ptr = watchdog_ptr(watchdog, offset);
    if (!ptr) {
        return -EINVAL;
    }

    __atomic_load(ptr, dest, __ATOMIC_RELAXED);

    return 0;
}

static int write32(struct shmlib_watchdog* const watchdog, const unsigned offset,
                            const uint32_t value)
{
    uint32_t* ptr = NULL;
    if (!watchdog) {
        return -EINVAL;
    }

    ptr = watchdog_ptr(watchdog, offset);
    if (!ptr) {
        return -EINVAL;
    }

    __atomic_store_n(ptr, value, __ATOMIC_RELAXED);

    return 0;
}

void shmlib_watchdog_init(struct shmlib_watchdog* watchdog, shmlib_wd_t mapping)
{
    if (!watchdog) {
        return;
    }

    watchdog->mapping = mapping;
    watchdog->enabled = true;
}

bool shmlib_watchdog_is_enabled(struct shmlib_watchdog* watchdog)
{
    if (!watchdog) {
        return false;
    }

    return watchdog->enabled;
}

int shmlib_watchdog_do_heartbeat(struct shmlib_watchdog* watchdog)
{
    int ret = 0;
    uint32_t value = 0;

    if (!watchdog) {
        return -EINVAL;
    }

    if (!watchdog->enabled) {
        return -EBUSY;
    }

    write32(watchdog, SHMLIB_WDG_REG_CTRL, SHMLIB_WDG_CTRL_RUNNING);

    ret = read32(watchdog, SHMLIB_WDG_REG_COUNTER_LO, &value);
    if (ret) {
        return ret;
    }

    /* Increase watchdog counter */
    value++;
    write32(watchdog, SHMLIB_WDG_REG_COUNTER_LO, value);

    /* Check for overflow condition */
    if (value == 0) {
        ret = read32(watchdog, SHMLIB_WDG_REG_COUNTER_HI, &value);
        if (ret) {
            return ret;
        }
        write32(watchdog, SHMLIB_WDG_REG_COUNTER_HI, value + 1);
    }

    return 0;
}
