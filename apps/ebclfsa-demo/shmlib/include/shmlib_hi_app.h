/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_HI_APP_H
#define SHMLIB_HI_APP_H

#include "shmlib_ringbuffer.h"
#include "shmlib_shm.h"

#define SHMLIB_HI_APP_UUID_LEN (37) /* 36 characters plus 1 NULL */

/**
 * @brief A shared memory buffer used for inter-process communication on shared memory.
 */
struct shmlib_hi_app {
    struct shmlib_ring_buffer hi_to_li;
    struct shmlib_ring_buffer li_to_hi;
    char uuid[SHMLIB_HI_APP_UUID_LEN];
};

/**
 * @brief Set the UUID of the HI app.
 *
 * @param hi_app Pointer to the HI app to set the UUID of.
 * @param name String containing the new UUID, must be COMLIB_HI_APP_UUID_LEN-1 characters.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -ENOSPC if the UUID is the wrong length.
 */
int shmlib_hi_app_set_uuid(struct shmlib_hi_app* hi_app, const char* uuid);

/**
 * @brief Clean up shared memory resources used by the app
 *
 * @return 0 if successful, error number if failed.
 */
int shmlib_hi_app_destroy(struct shmlib_hi_app* hi_app);

/**
 * @brief Create a new HI app with the given parameters.
 *
 * This will initialise the shared memory, allocate a new app based on the given name and UUID,
 * and set the optional shared memory pointer structs to their respective memory addresses.
 *
 * This is a convenience function which wraps a number of functions into an easily callable one.
 *
 * @param shm Pointer to the uninitialised shared memory struct.
 * @param uuid UUID of the new application.
 * @param app Pointer to where the new app should be stored.
 * @param hicom Pointer where the hicom SHM information should be stored. Can be NULL.
 * @param watchdog Pointer where the watchdog SHM information should be stored. Can be NULL.
 * @param init_proxyshm Boolean value representing whether the proxy SHM should be initialised (i.e.
 *                      wiped) before being used.
 *
 * @return Return 0 if successful, or error code on failure.
 */
int shmlib_hi_app_create_new(struct shmlib_shm* shm, const char* uuid,
                             struct shmlib_hi_app** app, struct shmlib_shm_ptr* hicom,
                             struct shmlib_shm_ptr* watchdog,
                             bool init_proxyshm);

#endif /* SHMLIB_HI_APP_H */
