/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>

#include "shmlib_shm.h"
#include "shmlib_logger.h"


typedef enum {
    ebclfsa_hv_shm_pc, /**< proxyshm */
    ebclfsa_hv_shm_wd, /**< watchdog */
    ebclfsa_hv_shm_hc, /**< hicom */
    ebclfsa_hv_shm_fb, /**< framebuffer, read-only for HI apps */
    ebclfsa_hv_shm_count
} ebclfsa_hv_shm_type_t;

/**
 * @brief Shared memory region configuration.
 */
struct shmlib_shm_region {
    uint64_t addr; /**< Address of shared memory region. */
    uint64_t size; /**< Size of shared memory region in bytes. */
    uint32_t type; /**< The shared memory region's type. */
    uint32_t pad;  /**< Keep 64 bit aligned. */
};

/**
 * @brief Shared memory configuration page details.
 */
struct shmlib_shm_region_header {
    uint32_t ident;        /**< Configuration header identifier. */
    uint32_t version;      /**< Version of shared memory configuration interface. */
    uint32_t region_count; /**< Number of region configurations which follow the header. */
    uint32_t pad;          /**< Align this header to 64 bits. */
    struct shmlib_shm_region region[]; /**< Use to access the regions which follow the header */
};

static const uint32_t SHM_CONFIG_IDENT = 0xe1fd0c6f;
static const uint32_t SHM_CONFIG_VERSION = 1;
static const void* SHM_REGION_ADDR = (void*)0x1234000000;


static int find_sharedmem_index(const struct shmlib_shm_region_header* const shm_header,
                                const ebclfsa_hv_shm_type_t type)
{
    if (type >= ebclfsa_hv_shm_count) {
        shmlib_log(SHMLIB_LOGGER_ERROR, "Invalid shm type: %d", type);
        return -EINVAL;
    }

    if (shm_header->ident != SHM_CONFIG_IDENT) {
        shmlib_log(SHMLIB_LOGGER_ERROR, "Ident in region_header: %x != expected: %x.",
                          shm_header->ident, SHM_CONFIG_IDENT);
        return -EIO;
    }

    if (shm_header->version != SHM_CONFIG_VERSION) {
        shmlib_log(SHMLIB_LOGGER_ERROR, "Version in region_header: %x != expected: %x.",
                          shm_header->version, SHM_CONFIG_VERSION);
        return -EIO;
    }

    for (int i = 0; i < (int)shm_header->region_count; ++i) {
        if (shm_header->region[i].type == type) {
            return i;
        }
    }
    return -ENOENT;
}

static int get_sharedmem(const struct shmlib_shm_region_header* const shm_header,
                         const struct shmlib_shm_region** dest, const ebclfsa_hv_shm_type_t type)
{
    int index = 0;

    if (!shm_header || !dest) {
        return -EINVAL;
    }

    index = find_sharedmem_index(shm_header, type);
    if (index < 0) {
        return index;
    }

    *dest = &(shm_header->region[index]);

    return 0;
}

static ssize_t get_region_by_type(const struct shmlib_shm_region_header* const shm_header,
                                             void** const dest, const ebclfsa_hv_shm_type_t type)
{
    int ret = 0;
    const struct shmlib_shm_region* shm = NULL;

    if (!dest) {
        return -EINVAL;
    }

    ret = get_sharedmem(shm_header, &shm, type);
    if (ret) {
        shmlib_log_with_error_code(ret, "No shm config found");
        return ret;
    }

    *dest = (void*)shm->addr;
    return (ssize_t)shm->size;
}

int shmlib_shm_get_proxyshm(struct shmlib_shm* const shm, struct shmlib_shm_ptr* const dest)
{
    ssize_t ret = 0;
    void* ptr = NULL;

    if (!shm || !dest) {
        return -EINVAL;
    }

    if (!shm->header) {
        return -EIO;
    }

    ret = get_region_by_type(shm->header, &ptr, ebclfsa_hv_shm_pc);
    if (ret < 0) {
        return (int)ret;
    }

    dest->size = ret;
    dest->proxyshm = ptr;

    return 0;
}

int shmlib_shm_get_watchdog(struct shmlib_shm* const shm, struct shmlib_shm_ptr* const dest)
{
    ssize_t ret = 0;
    void* ptr = NULL;

    if (!shm || !dest) {
        return -EINVAL;
    }

    if (!shm->header) {
        return -EIO;
    }

    ret = get_region_by_type(shm->header, &ptr, ebclfsa_hv_shm_wd);
    if (ret < 0) {
        return (int)ret;
    }

    dest->size = ret;
    dest->watchdog = ptr;

    return 0;
}

int shmlib_shm_get_hicom(struct shmlib_shm* const shm, struct shmlib_shm_ptr* const dest)
{
    ssize_t ret = 0;
    void* ptr = NULL;

    if (!shm || !dest) {
        return -EINVAL;
    }

    if (!shm->header) {
        return -EIO;
    }

    ret = get_region_by_type(shm->header, &ptr, ebclfsa_hv_shm_hc);
    if (ret < 0) {
        return (int)ret;
    }

    dest->size = ret;
    dest->hicom = ptr;

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

    if (!shm->header) {
        return -EIO;
    }

    ret = get_region_by_type(shm->header, &ptr, ebclfsa_hv_shm_fb);
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

    shm->header = SHM_REGION_ADDR;

    return 0;
}

int shmlib_shm_deinit(struct shmlib_shm* const shm)
{
    if (!shm) {
        return -EINVAL;
    }

    return 0;
}
