/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_SHM_H
#define SHMLIB_SHM_H

#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>

#include "shmlib_watchdog.h"

typedef uint8_t* shmlib_fb_t;
typedef uint8_t* shmlib_hicom_t;

#ifndef BUILD_HI
enum shmlib_shm_type {
    SHMLIB_SHM_TYPE_PROXYSHM,
    SHMLIB_SHM_TYPE_FRAMEBUFFER,
    SHMLIB_SHM_TYPE_MAX,
};

struct shmlib_shm_mapping {
    void* ptr;
    size_t len;
};
#endif


struct shmlib_shm {
#ifdef BUILD_HI
    const struct shmlib_shm_region_header* header;
#else
    struct shmlib_shm_mapping mappings[SHMLIB_SHM_TYPE_MAX];
#endif
};

struct shmlib_shm_ptr {
    union {
        struct shmlib_proxyshm* proxyshm;
        shmlib_wd_t watchdog;
        shmlib_hicom_t hicom;
        shmlib_fb_t framebuffer;
    };
    size_t size;
};

/**
 * @brief Return a pointer to the proxyshm shared memory.
 *
 * The shmlib_shm must have been previously initialised by shmlib_shm_init().
 * This function is supported in all modes.
 *
 * @param shm Pointer to the initialised shared memory struct.
 * @param dest Pointer to where the result should be stored.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EIO if an IO error occurred.
 *          - -ENOTSUP if the given mode is not supported by the library.
 *          - -EPERM if access is denied.
 */
int shmlib_shm_get_proxyshm(struct shmlib_shm* shm, struct shmlib_shm_ptr* dest);

#ifdef BUILD_HI
/**
 * @brief Return a pointer to the watchdog shared memory.
 *
 * The shmlib_shm must have been previously initialised by shmlib_shm_init().
 *
 * @param shm Pointer to the initialised shared memory struct.
 * @param dest Pointer to where the result should be stored.
 *
 * @return Return the size of the memory region if successful, or one of the following error codes
 *         on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EIO if an IO error occurred.
 *          - -ENOTSUP if the given mode is not supported by the library.
 *          - -EPERM if access is denied.
 */
int shmlib_shm_get_watchdog(struct shmlib_shm* shm, struct shmlib_shm_ptr* dest);

/**
 * @brief Return a pointer to the shared memory between HI applications.
 *
 * The shmlib_shm must have been previously initialised by shmlib_shm_init().
 *
 * @param shm Pointer to the initialised shared memory struct.
 * @param dest Pointer to where the result should be stored.
 *
 * @return Return the size of the memory region if successful, or one of the following error codes
 *         on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EIO if an IO error occurred.
 *          - -ENOTSUP if the given mode is not supported by the library.
 *          - -EPERM if access is denied.
 */
int shmlib_shm_get_hicom(struct shmlib_shm* shm, struct shmlib_shm_ptr* dest);
#endif

/**
 * @brief Return a pointer to the shared memory of the framebuffer.
 *
 * The shmlib_shm must have been previously initialised by shmlib_shm_init().
 * This function is supported in all modes.
 *
 * @param shm Pointer to the initialised shared memory struct.
 * @param dest Pointer to where the result should be stored.
 *
 * @return Return the size of the memory region if successful, or one of the following error codes
 *         on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EIO if an IO error occurred.
 *          - -ENOTSUP if the given mode is not supported by the library.
 *          - -EPERM if access is denied.
 */
int shmlib_shm_get_framebuffer(struct shmlib_shm* shm, struct shmlib_shm_ptr* dest);

/**
 * @brief Initialise the given shared memory struct.
 *
 * The mode variable inside the struct must be set before calling this function.
 *
 * @param shm Pointer to the shm struct to initialise.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -ENOTSUP if the given mode is not supported by the library.
 */
int shmlib_shm_init(struct shmlib_shm* shm);

/**
 * @brief Deinitialise the given shared memory struct.
 *
 * The struct must have been previously initialised by calling shmlib_shm_init().
 *
 * @param shm Pointer to the shm struct to deinitialise.
 *
 * @return Return 0 if successful, or one of the following error codes on failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -ENOTSUP if the given mode is not supported by the library.
 */
int shmlib_shm_deinit(struct shmlib_shm* shm);

/**
 * @brief Copy len bytes from src to dest.
 *
 * strncpy and memcpy seem to have issues with memory alignment when
 * reading and writing to the shared memory regions on real hardware (they
 * probably try to be clever and optimise the accesses in ways that break
 * alignment), resulting in SIGBUS and the program crashing.
 * We can use a very simple byte-for-byte copy here to work around this
 * problem and declare them as volatile to stop the compiler from trying
 * to optimise it.
 *
 * @param dest Destination buffer (must have at least len bytes available).
 * @param src Source buffer (must be at least len bytes).
 * @param len Number of bytes to copy.
 *
 * @return Return 0 if successful, or -EINVAL if invalid arguments were passed.
 */
int shmlib_shm_copy_bytes(volatile char* dest, volatile const char* src, size_t len);

#endif /* SHMLIB_SHM_H */
