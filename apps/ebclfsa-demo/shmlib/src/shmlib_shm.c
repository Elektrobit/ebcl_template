/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <stddef.h>
#include <errno.h>

int shmlib_shm_copy_bytes(volatile char* const dest, volatile const char* const src,
                          const size_t len)
{
    if (!dest || !src) {
        return -EINVAL;
    }

    for (size_t i = 0; i < len; i++) {
        dest[i] = src[i];
    }

    return 0;
}
