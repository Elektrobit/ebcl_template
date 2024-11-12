/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_LOCK_H
#define SHMLIB_LOCK_H

#include <stdbool.h>

typedef int shmlib_spinlock_t;

/**
 * @brief Locks a spinlock object.
 *
 * This function acquires a spinlock object by using the atomic compare-and-exchange operation.
 * It spins in a loop while waiting for the lock to become available.
 *
 * @param lock Pointer to the spinlock object to lock.
 *
 * @return None
 */
void shmlib_spin_lock(shmlib_spinlock_t* lock);

/**
 * @brief Unlocks a spinlock object.
 *
 * This function releases a spinlock object by using the atomic compare-and-exchange operation.
 * It spins in a loop while waiting for the lock to become available.
 *
 * @param lock Pointer to the spinlock object to unlock.
 *
 * @return None.
 */
void shmlib_spin_unlock(shmlib_spinlock_t* lock);

/**
 * @brief Check if the lock is currently locked.
 *
 * @param lock Pointer to the spinlock object to check.
 *
 * @return true if the lock is locked, false if it is unlocked.
 */
bool shmlib_spin_is_locked(const shmlib_spinlock_t* lock);

#endif /* SHMLIB_LOCK_H */
