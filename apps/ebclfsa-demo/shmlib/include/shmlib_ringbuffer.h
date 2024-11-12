/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_RINGBUFFER_H
#define SHMLIB_RINGBUFFER_H

#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/types.h>

#include "shmlib_lock.h"

#define SHMLIB_RING_BUFFER_SIZE 4096
#define SHMLIB_RING_BUF_MAX_DATA_LEN (SHMLIB_RING_BUFFER_SIZE - 1)

struct shmlib_ring_buffer {
    size_t head;
    size_t tail;
    shmlib_spinlock_t lock;
    char buffer[SHMLIB_RING_BUFFER_SIZE];
};

/**
 * @brief Writes data to a ring buffer.
 *
 * @param buffer The ring buffer to write to.
 * @param data The data to write.
 * @param len The length of data to write.
 *
 * @return Return the amount of data written if successful, or one of the following error codes on
 *         failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -ENOSPC if the data is too large to send.
 */
ssize_t shmlib_ring_buffer_write(struct shmlib_ring_buffer* buffer, const char* data, size_t len);

/**
 * @brief Reads data from a ring buffer.
 *
 * @param buffer The ring buffer to read from.
 * @param dest Pointer where the read data should be copied to.
 * @param dest_len Maximum length of the destination buffer.
 *
 * @return Return the amount of data read if successful, or one of the following error codes on
 *         failure:
 *          - -EINVAL if invalid arguments were passed.
 *          - -EAGAIN if no data was available.
 */
ssize_t shmlib_ring_buffer_read(struct shmlib_ring_buffer* buffer, char* dest, size_t dest_len);

/**
 * @brief Check if the given ring buffer has data available to be read.
 *
 * @param buffer The ring buffer to check.
 *
 * @return Return 1 if data is available, 0 if no data, or -EINVAL if invalid arguments were passed.
 */
int shmlib_ring_buffer_data_available(struct shmlib_ring_buffer* buffer);

#endif /* SHMLIB_RINGBUFFER_H */
