/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>
#include <stdatomic.h>
#include <string.h>

#include "shmlib_hi_app.h"
#include "shmlib_logger.h"
#include "shmlib_proxyshm.h"
#include "shmlib_shm.h"


int shmlib_hi_app_set_uuid(struct shmlib_hi_app* const hi_app, const char* const uuid)
{
    if (!hi_app || !uuid) {
        return -EINVAL;
    }

    if (strnlen(uuid, sizeof(hi_app->uuid)) != sizeof(hi_app->uuid) - 1 &&
        strnlen(uuid, sizeof(hi_app->uuid)) != 0) {
        return -EINVAL;
    }

    return shmlib_shm_copy_bytes(hi_app->uuid, uuid, sizeof(hi_app->uuid));
}

int shmlib_hi_app_destroy(struct shmlib_hi_app* const hi_app)
{
    int ret = 0;
    static const char blank_uuid[sizeof(hi_app->uuid)] = {'\0'};

    if (!hi_app) {
        return -EINVAL;
    }

    ret = shmlib_hi_app_set_uuid(hi_app, blank_uuid);
    if (ret) {
        return ret;
    }

    memset(&hi_app->li_to_hi, 0x0, sizeof(hi_app->li_to_hi));
    memset(&hi_app->hi_to_li, 0x0, sizeof(hi_app->hi_to_li));

    return 0;
}

#ifdef BUILD_HI

int shmlib_hi_app_create_new(struct shmlib_shm* const shm, const char* const uuid,
                             struct shmlib_hi_app** const app,
                             struct shmlib_shm_ptr* const hicom,
                             struct shmlib_shm_ptr* const watchdog,
                             const bool init_proxyshm
                            )

{
    struct shmlib_shm_ptr proxyshm = {0};
    int ret = 0;

    if (!shm || !uuid || !app) {
        return -EINVAL;
    }

    ret = shmlib_shm_init(shm);
    if (ret) {
        return ret;
    }

    ret = shmlib_shm_get_proxyshm(shm, &proxyshm);
    if (ret) {
        return ret;
    }

    if (init_proxyshm) {
        ret = shmlib_proxyshm_init_proxyshm(&proxyshm);
        if (ret) {
            return ret;
        }
    }

    *app = shmlib_proxyshm_allocate_app(&proxyshm, uuid);
    if (!*app) {
        return -ENOMEM;
    }

    if (hicom) {
        ret = shmlib_shm_get_hicom(shm, hicom);
        if (ret) {
            shmlib_log_function_failed("shmlib_shm_get_hicom", ret);
            return ret;
        }
    }

    if (watchdog) {
        ret = shmlib_shm_get_watchdog(shm, watchdog);
        if (ret) {
            shmlib_log_function_failed("shmlib_shm_get_watchdog", ret);
            return ret;
        }
    }

    return 0;
}

#endif
