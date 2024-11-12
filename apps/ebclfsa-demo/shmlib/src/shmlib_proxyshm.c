/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#include "shmlib_proxyshm.h"
#include "shmlib_lock.h"
#include "shmlib_logger.h"

#define MAX_SHM_APPS(proxyshm) ((proxyshm)->size / sizeof(struct shmlib_hi_app))

static const char blank_uuid[SHMLIB_HI_APP_UUID_LEN] = {'\0'};

struct shmlib_proxyshm {
    shmlib_spinlock_t lock;
    struct shmlib_hi_app shm[];
};

void shmlib_proxyshm_lock(struct shmlib_shm_ptr* const proxyshm)
{
    if (!proxyshm || !proxyshm->proxyshm) {
        return;
    }

    shmlib_spin_lock(&proxyshm->proxyshm->lock);
}

void shmlib_proxyshm_unlock(struct shmlib_shm_ptr* const proxyshm)
{
    if (!proxyshm || !proxyshm->proxyshm) {
        return;
    }

    shmlib_spin_unlock(&proxyshm->proxyshm->lock);
}

bool shmlib_proxyshm_is_locked(const struct shmlib_shm_ptr* const proxyshm)
{
    if (!proxyshm || !proxyshm->proxyshm) {
        return false;
    }

    return shmlib_spin_is_locked(&proxyshm->proxyshm->lock);
}

int shmlib_proxyshm_find_app(const struct shmlib_shm_ptr* const proxyshm, const char* const uuid,
                             struct shmlib_hi_app** const app)
{
    if (!proxyshm || !uuid) {
        return -EINVAL;
    }

    if (!shmlib_proxyshm_is_locked(proxyshm)) {
        return -EPERM;
    }

    for (uint64_t i = 0; i < MAX_SHM_APPS(proxyshm); i++) {
        /* If the UUID is blank, this slot isn't being used */
        if (!memcmp(uuid, proxyshm->proxyshm->shm[i].uuid,
                    sizeof(proxyshm->proxyshm->shm[i].uuid))) {
            if (app) {
                *app = &proxyshm->proxyshm->shm[i];
            }
            return 0;
        }
    }

    return -ENOENT;
}

int shmlib_proxyshm_find_next_empty_app_slot(const struct shmlib_shm_ptr* const proxyshm,
                                             struct shmlib_hi_app** const app)
{
    return shmlib_proxyshm_find_app(proxyshm, blank_uuid, app);
}

struct shmlib_hi_app* shmlib_proxyshm_get_app_shm(const struct shmlib_shm_ptr* const proxyshm,
                                                  const uint32_t index)
{
    if (!proxyshm || index >= MAX_SHM_APPS(proxyshm)) {
        return NULL;
    }

    return &proxyshm->proxyshm->shm[index];
}

int shmlib_proxyshm_init_proxyshm(struct shmlib_shm_ptr* const proxyshm)
{
    int ret = 0;
    size_t counter = 0;
    struct shmlib_hi_app* app = NULL;

    if (!proxyshm) {
        return -EINVAL;
    }

    shmlib_proxyshm_lock(proxyshm);

    while ((app = shmlib_proxyshm_get_app_shm(proxyshm, counter++)) != NULL) {
        ret = shmlib_hi_app_destroy(app);
        if (ret) {
            break;
        }
    }

    shmlib_proxyshm_unlock(proxyshm);

    return ret;
}

struct shmlib_hi_app* shmlib_proxyshm_allocate_app(struct shmlib_shm_ptr* const proxyshm, const char* const uuid)
{
    struct shmlib_hi_app* hi_app = NULL;
    int ret = 0;

    if (!proxyshm) {
        return NULL;
    }

    shmlib_proxyshm_lock(proxyshm);

    ret = shmlib_proxyshm_find_next_empty_app_slot(proxyshm, &hi_app);
    if (ret) {
        shmlib_log_with_error_code(ret, "Error finding a new HI app slot");
        goto fail;
    }

    ret = shmlib_hi_app_set_uuid(hi_app, uuid);
    if (ret) {
        shmlib_log_with_error_code(ret, "Error setting new HI app's uuid");
        goto fail;
    }

    shmlib_proxyshm_unlock(proxyshm);

    return hi_app;

fail:
    if (hi_app) {
        shmlib_hi_app_destroy(hi_app);
    }

    shmlib_proxyshm_unlock(proxyshm);

    return NULL;
}
