/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "shmlib_ringbuffer.h"

static ssize_t read_bytes(struct shmlib_ring_buffer* const buffer,
                                             char* const dest, size_t dest_len)
{
    size_t index = 0;

    if (!buffer || !dest) {
        return -EINVAL;
    }

    if (dest_len >= SHMLIB_RING_BUFFER_SIZE) {
        dest_len = SHMLIB_RING_BUFFER_SIZE;
    }

    for (index = 0; index < dest_len; index++) {
        if (!shmlib_ring_buffer_data_available(buffer)) {
            break;
        }
        dest[index] = buffer->buffer[buffer->tail];
        buffer->tail = (buffer->tail + 1) % SHMLIB_RING_BUFFER_SIZE;
    }

    return (ssize_t)index;
}


static ssize_t bytes_remaining(const struct shmlib_ring_buffer* const buffer)
{
    size_t head = 0;
    size_t tail = 0;

    if (!buffer) {
        return -EINVAL;
    }

    head = buffer->head % SHMLIB_RING_BUFFER_SIZE;
    tail = buffer->tail % SHMLIB_RING_BUFFER_SIZE;

    if (head > tail) {
        /* Write head has advanced but not wrapped around */
        return SHMLIB_RING_BUFFER_SIZE - head + tail - 1;
    }

    if (head < tail) {
        /* Write head has wrapped around */
        return (ssize_t)tail - (ssize_t)head - 1;
    }

    /* head == tail */
    return SHMLIB_RING_BUF_MAX_DATA_LEN;
}

ssize_t shmlib_ring_buffer_write(struct shmlib_ring_buffer* const buffer, const char* const data,
                                 const size_t len)
{
    ssize_t remaining = 0;
    if (!buffer || !data) {
        return -EINVAL;
    }

    shmlib_spin_lock(&buffer->lock);

    remaining = bytes_remaining(buffer);
    if (remaining < 0) {
        return remaining;
    }

    if (len > (size_t)remaining) {
        shmlib_spin_unlock(&buffer->lock);
        return -ENOSPC;
    }

    for (size_t i = 0; i < len; i++) {
        buffer->buffer[buffer->head] = data[i];
        buffer->head = (buffer->head + 1) % SHMLIB_RING_BUFFER_SIZE;
    }

    shmlib_spin_unlock(&buffer->lock);

    return (ssize_t)len;
}

ssize_t shmlib_ring_buffer_read(struct shmlib_ring_buffer* const buffer, char* const dest,
                                size_t dest_len)
{
    ssize_t ret = 0;

    if (!buffer || !dest) {
        return -EINVAL;
    }

    shmlib_spin_lock(&buffer->lock);

    if (!shmlib_ring_buffer_data_available(buffer)) {
        shmlib_spin_unlock(&buffer->lock);
        return -EAGAIN;
    }

    ret = read_bytes(buffer, dest, dest_len);

    shmlib_spin_unlock(&buffer->lock);

    return ret;
}

int shmlib_ring_buffer_data_available(struct shmlib_ring_buffer* const buffer)
{
    if (!buffer) {
        return -EINVAL;
    }

    return buffer->tail != buffer->head;
}
