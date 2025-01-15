/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <sys/mman.h>

#include "shmlib_logger.h"
#include "shmlib_shm.h"

#define BASE_PATH "/sys/firmware/devicetree/base/reserved-memory"

static const char* get_shm_label(const enum shmlib_shm_type type)
{
    switch (type) {
    case SHMLIB_SHM_TYPE_PROXYSHM:
        return "hv_proxycomshm";
    case SHMLIB_SHM_TYPE_FRAMEBUFFER:
        return "hv_fbshm";
    default:
        shmlib_log(SHMLIB_LOGGER_ERROR, "Invalid shared memory type: %d", type);
        return NULL;
    }
}

static const char* get_shm_path(const struct shmlib_shm* const shm,
                                const enum shmlib_shm_type type)
{
    static char path[PATH_MAX] = {'\0'};
    const char* shm_name = NULL;

    if (!shm) {
        return NULL;
    }

    switch (type) {
    case SHMLIB_SHM_TYPE_PROXYSHM:
        shm_name = "hv_proxycomshm@9100000";
        break;
    case SHMLIB_SHM_TYPE_FRAMEBUFFER:
        shm_name = "hv_fbshm@9500000";
        break;
    default:
        shmlib_log(SHMLIB_LOGGER_ERROR, "Invalid shared memory type: %d", type);
        return NULL;
    }

    (void)snprintf(path, sizeof(path), "%s/%s/reg", BASE_PATH, shm_name);

    return path;
}

static void* mmap_shm(size_t length, uint64_t offset)
{
    int shm_fd = open("/dev/mem", O_RDWR | O_SYNC | O_CLOEXEC);
    shmlib_log(SHMLIB_LOGGER_DEBUG, "Opened /dev/mem: %d", shm_fd);
    void* mapping = mmap(0, length, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, (off_t)offset);
    if (mapping == MAP_FAILED) {
        shmlib_log_function_failed(__func__, errno);
        /**
         * Set this to NULL rather than MAP_FAILED so that functions checking
         * this result do not have to have that value defined.
         */
        mapping = NULL;
    }
    else {
        shmlib_log(SHMLIB_LOGGER_DEBUG, "Mapped shared memory: 0x%016lx",
                          (uintptr_t)mapping);
    }
    close(shm_fd);
    return mapping;
}

static ssize_t read_shm_addr_from_file(const char* file, uint64_t* base_addr, size_t* size)
{
    uint64_t addr_size[2] = {0};
    ssize_t ret = 0;
    int file_fd = 0;

    if (file == NULL) {
        return -EINVAL;
    }

    file_fd = open(file, O_RDONLY | O_CLOEXEC);
    if (file_fd < 0) {
        shmlib_log_with_error_code(errno, "Could not open file \"%s\"", file);
        return -errno;
    }

    ret = read(file_fd, addr_size, sizeof(addr_size));
    if (ret < 0) {
        shmlib_log_function_failed("read", errno);
        ret = -errno;
        goto close;
    }

    if (ret < (ssize_t)sizeof(addr_size)) {
        shmlib_log(
            SHMLIB_LOGGER_ERROR,
            "Could not read the expected number of bytes from %s (wanted %lu, got %lu)", file, ret,
            sizeof(addr_size));
        ret = -EIO;
        goto close;
    }

    /* Device tree integers are stored big-endian */
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    *base_addr = __builtin_bswap64(addr_size[0]);
    *size = __builtin_bswap64(addr_size[1]);
#else
    *base_addr = addr_size[0];
    *size = addr_size[1];
#endif

    ret = 0;

close:
    close(file_fd);

    return ret;
}

static ssize_t create_shm_mapping(const struct shmlib_shm* const shm,
                                  const enum shmlib_shm_type type, void** dest)
{
    uint64_t base_addr = 0;
    size_t size = 0;
    ssize_t ret = 0;

    if (!shm || !dest || type >= SHMLIB_SHM_TYPE_MAX) {
        return -EINVAL;
    }

    ret = read_shm_addr_from_file(get_shm_path(shm, type), &base_addr, &size);
    if (ret) {
        return ret;
    }

    shmlib_log(SHMLIB_LOGGER_DEBUG, "Base addr of %s is: 0x%08lx - 0x%08lx",
                      get_shm_label(type), base_addr, base_addr + size - 1);

    ret = (ssize_t)size;

    *dest = mmap_shm(size, base_addr);
    if (!*dest) {
        return -EIO;
    }

    return ret;
}

static ssize_t get_shm_mapping(const struct shmlib_shm* const shm,
                               const enum shmlib_shm_type type, void** dest)
{
    if (type >= SHMLIB_SHM_TYPE_MAX || !dest || !shm) {
        return -EINVAL;
    }

    if (!shm->mappings[type].ptr) {
        return -EIO;
    }

    *dest = shm->mappings[type].ptr;
    return (ssize_t)shm->mappings[type].len;
}

int shmlib_shm_get_proxyshm(struct shmlib_shm* const shm, struct shmlib_shm_ptr* const dest)
{
    ssize_t ret = 0;
    void* ptr = NULL;

    if (!shm || !dest) {
        return -EINVAL;
    }

    ret = get_shm_mapping(shm, SHMLIB_SHM_TYPE_PROXYSHM, &ptr);
    if (ret < 0) {
        return (int)ret;
    }

    dest->size = ret;
    dest->proxyshm = ptr;

    return 0;
}

int shmlib_shm_get_framebuffer(struct shmlib_shm* const shm,
                                  struct shmlib_shm_ptr* const dest)
{
    ssize_t ret = 0;
    void* ptr = NULL;

    if (!shm || !dest) {
        return -EINVAL;
    }

    ret = get_shm_mapping(shm, SHMLIB_SHM_TYPE_FRAMEBUFFER, &ptr);
    if (ret < 0) {
        return (int)ret;
    }

    dest->size = ret;
    dest->framebuffer = ptr;

    return 0;
}

int shmlib_shm_init(struct shmlib_shm* const shm)
{
    if (!shm) {
        return -EINVAL;
    }

    for (size_t i = 0; i < SHMLIB_SHM_TYPE_MAX; i++) {
        void* ptr = NULL;
        ssize_t len = create_shm_mapping(shm, i, &ptr);
        if (len >= 0) {
            shm->mappings[i].len = len;
            shm->mappings[i].ptr = ptr;
        }
    }

    return 0;
}

int shmlib_shm_deinit(struct shmlib_shm* const shm)
{
    if (!shm) {
        return -EINVAL;
    }

    for (size_t i = 0; i < SHMLIB_SHM_TYPE_MAX; i++) {
        if (shm->mappings[i].ptr) {
            munmap(shm->mappings[i].ptr, shm->mappings[i].len);
        }
    }

    return 0;
}
