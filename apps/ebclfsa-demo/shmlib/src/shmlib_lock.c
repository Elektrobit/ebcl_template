/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <stdatomic.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>

#include "shmlib_lock.h"

static const time_t SHMLIB_LOCK_WAIT_NS = 100000; /**< 100us in nanoseconds */

void shmlib_spin_lock(shmlib_spinlock_t* const lock)
{
    int expected = 0;
    while (!__atomic_compare_exchange_n(lock, &expected, 1, false, __ATOMIC_ACQUIRE,
                                        __ATOMIC_RELAXED)) {
        struct timespec sleep_time = {0, SHMLIB_LOCK_WAIT_NS};
        nanosleep(&sleep_time, NULL);
        expected = 0;
    }
}

void shmlib_spin_unlock(shmlib_spinlock_t* const lock)
{
    __atomic_store_n(lock, 0, __ATOMIC_RELEASE);
}

bool shmlib_spin_is_locked(const shmlib_spinlock_t* const lock)
{
    return !!__atomic_load_n(lock, __ATOMIC_ACQUIRE);
}
