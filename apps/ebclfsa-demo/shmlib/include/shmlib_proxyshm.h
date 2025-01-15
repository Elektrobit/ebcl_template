/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_PROXYSHM_H
#define SHMLIB_PROXYSHM_H

#include <stdbool.h>
#include <unistd.h>

#include "shmlib_hi_app.h"
#include "shmlib_shm.h"

struct shmlib_proxyshm;

/**
 * @brief Return the shmlib_hi_app at the given index inside the shm buffer.
 *
 * @param proxyshm Pointer and size of the proxyshm
 * @param index Index of the shmlib_hi_app inside the proxyshm
 *
 * @return Return the pointer to the desired shmlib_hi_app, or NULL if not found.
 */
struct shmlib_hi_app* shmlib_proxyshm_get_app_shm(const struct shmlib_shm_ptr* proxyshm, uint32_t index);

/**
 * @brief Lock the given proxyshm.
 *
 * @param proxyshm Pointer and size of the proxyshm
 */
void shmlib_proxyshm_lock(struct shmlib_shm_ptr* proxyshm);

/**
 * @brief Unlock the given proxyshm.
 *
 * @param proxyshm Pointer and size of the proxyshm
 */
void shmlib_proxyshm_unlock(struct shmlib_shm_ptr* proxyshm);

/**
 * @brief Check if the lock is currently locked.
 *
 * @param proxyshm Pointer and size of the proxyshm
 *
 * @return true if the lock is locked, false if it is unlocked.
 */
bool shmlib_proxyshm_is_locked(const struct shmlib_shm_ptr* proxyshm);

/**
 * @brief Find the HI app matching the given UUID in the shared memory buffer.
 *
 * Must be called in a locked context (i.e. shmlib_proxyshm_lock must have been previously called).
 *
 * @param proxyshm Pointer and size of the proxyshm
 * @param uuid UUID of the HI app to search for.
 * @param app Pointer where the pointer to the found app should be placed. Can be NULL.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EPERM if the shared memory buffer is not locked.
 *          - -ENOENT if the app was not found.
 */
int shmlib_proxyshm_find_app(const struct shmlib_shm_ptr* proxyshm, const char* uuid,
                             struct shmlib_hi_app** app);

/**
 * @brief Search through the shared memory region and find the next free HI app slot.
 *
 * Must be called in a locked context (i.e. shmlib_proxyshm_lock must have been previously called).
 *
 * @param proxyshm Pointer and size of the proxyshm
 * @param shm_size size of the shared memory region.
 * @param app Pointer where the pointer to the free app slot should be placed.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EPERM if the shared memory buffer is not locked.
 *          - -ENOENT if the app was not found.
 */
int shmlib_proxyshm_find_next_empty_app_slot(const struct shmlib_shm_ptr* proxyshm,
                                             struct shmlib_hi_app** app);

/**
 * @brief Destroys any and all remnants of any apps in the shared memory region.
 *
 * @param proxyshm Pointer and size of the proxyshm
 * @param max_size size of the shared memory region.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 */
int shmlib_proxyshm_init_proxyshm(struct shmlib_shm_ptr* proxyshm);

/**
 * @brief Allocate a section of the shared memory for a new HI application.
 *
 * @param proxyshm Pointer and size of the proxyshm
 * @param uuid UUID of the new application
 *
 * @return Return a pointer to the shared memory between HI and proxy application, or NULL
 *         in case of an error.
 */
struct shmlib_hi_app* shmlib_proxyshm_allocate_app(struct shmlib_shm_ptr* proxyshm, const char* uuid);


#endif /* SHMLIB_PROXYSHM_H */
