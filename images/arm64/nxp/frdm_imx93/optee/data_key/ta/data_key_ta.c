
/*
 * data_key_ta.c
 * Minimal OP-TEE TA for LUKS key wrapping/unwrapping and self-test.
 * License: BSD-2-Clause
 */

#include <tee_internal_api.h>
#include <tee_internal_api_extensions.h>
// #include <trace.h> /* provides IMSG(), EMSG() */
#include <string.h>
#include "data_key_ta.h"

/* ===== Configuration ===== */

/* Persistent object name for the KEK; stored in OP-TEE Secure Storage */
#define KEK_OBJ_ID "kek.bin"
#define KEK_BITS 256

/* Storage backend: TEE_STORAGE_PRIVATE selects REE FS (preferred) or RPMB FS by config.
 * If you want to force RPMB and your platform is provisioned, use TEE_STORAGE_PRIVATE_RPMB.
 */
static const uint32_t storage_id = TEE_STORAGE_PRIVATE;

/* ===== KEK handling (Secure Storage) ===== */

static TEE_Result get_or_create_kek(uint8_t *kek, size_t kek_len)
{
    TEE_ObjectHandle oh = TEE_HANDLE_NULL;
    TEE_Result res = TEE_ERROR_GENERIC;
    bool kek_present = false;

    /* Try opening an existing KEK object */
    res = TEE_OpenPersistentObject(storage_id, KEK_OBJ_ID, strlen(KEK_OBJ_ID),
                                   TEE_DATA_FLAG_ACCESS_READ | TEE_DATA_FLAG_ACCESS_WRITE,
                                   &oh);
    if (res == TEE_SUCCESS)
    {
        uint32_t read_bytes = 0;
        kek_present = true; // kek found

        res = TEE_ReadObjectData(oh, kek, (uint32_t)kek_len, &read_bytes);

        TEE_CloseObject(oh);
        if ((res == TEE_SUCCESS) && (read_bytes != kek_len))
        {
            res = TEE_ERROR_GENERIC;
        }
    }
    if (kek_present == false)
    {
        /* Create a new KEK and persist it */
        TEE_GenerateRandom(kek, kek_len);

        res = TEE_CreatePersistentObject(storage_id, KEK_OBJ_ID, strlen(KEK_OBJ_ID),
                                         TEE_DATA_FLAG_ACCESS_READ | TEE_DATA_FLAG_ACCESS_WRITE |
                                             TEE_DATA_FLAG_OVERWRITE,
                                         TEE_HANDLE_NULL, kek, (uint32_t)kek_len, &oh);
        if (res == TEE_SUCCESS)
        {
            TEE_CloseObject(oh);
        }
    }

    return res;
}

/* ===== AES-GCM helpers =====
 * Layout for wrapped blob: IV(12) | TAG(16) | CIPHERTEXT
 */

static TEE_Result aes_gcm_encrypt(const uint8_t *kek, size_t kek_len,
                                  const void *in_buf, size_t in_len,
                                  void *out_buf, size_t *out_len)
{
    TEE_OperationHandle op = TEE_HANDLE_NULL;
    TEE_ObjectHandle key = TEE_HANDLE_NULL;
    TEE_Result res = TEE_SUCCESS;

    uint8_t iv[12];
    uint8_t tag[16];
    uint32_t tag_len = sizeof(tag) * 8;
    uint32_t dst_len = (uint32_t)in_len; /* ciphertext size equals plaintext size */

    if (*out_len < (sizeof(iv) + sizeof(tag) + in_len))
    {
        res = TEE_ERROR_SHORT_BUFFER;
    }

    if (res == TEE_SUCCESS)
    {
        /* Prepare transient key object */
        res = TEE_AllocateTransientObject(TEE_TYPE_AES, KEK_BITS, &key);
    }
    if (res == TEE_SUCCESS)
    {
        TEE_Attribute attr;
        TEE_InitRefAttribute(&attr, TEE_ATTR_SECRET_VALUE, kek, kek_len);
        res = TEE_PopulateTransientObject(key, &attr, 1);
    }

    if (res == TEE_SUCCESS)
    {
        /* Allocate operation */
        res = TEE_AllocateOperation(&op, TEE_ALG_AES_GCM, TEE_MODE_ENCRYPT, KEK_BITS);
    }
    if (res == TEE_SUCCESS)
    {
        res = TEE_SetOperationKey(op, key);
    }
    if (res == TEE_SUCCESS)
    {

        TEE_GenerateRandom(iv, sizeof(iv));
        TEE_AEInit(op, iv, sizeof(iv), tag_len, 0, in_len);

        TEE_OperationInfo info;
        TEE_GetOperationInfo(op, &info);

        /* Encrypt to out_buf + IV+TAG offset */
        res = TEE_AEEncryptFinal(op,
                                 (void *)in_buf, (uint32_t)in_len,
                                 (uint8_t *)out_buf + sizeof(iv) + sizeof(tag), &dst_len,
                                 tag, &tag_len);
    }
    if (res == TEE_SUCCESS)
    {
        /* Layout: IV | TAG | CIPHERTEXT */
        TEE_MemMove(out_buf, iv, sizeof(iv));
        TEE_MemMove((uint8_t *)out_buf + sizeof(iv), tag, sizeof(tag));
        *out_len = sizeof(iv) + sizeof(tag) + dst_len;
    }
    if (op)
        TEE_FreeOperation(op);
    if (key)
        TEE_FreeTransientObject(key);
    return res;
}

static TEE_Result aes_gcm_decrypt(const uint8_t *kek, size_t kek_len,
                                  const void *in_buf, size_t in_len,
                                  void *out_buf, size_t *out_len)
{
    if (in_len < (12 + 16))
        return TEE_ERROR_BAD_PARAMETERS;

    const uint8_t *iv = (const uint8_t *)in_buf;
    uint8_t *tag = (uint8_t *)((const uint8_t *)in_buf + 12);
    const uint8_t *ct = (const uint8_t *)in_buf + 12 + 16;
    size_t ct_len = in_len - (12 + 16);

    TEE_OperationHandle op = TEE_HANDLE_NULL;
    TEE_ObjectHandle key = TEE_HANDLE_NULL;
    TEE_Result res = TEE_SUCCESS;

    uint32_t dst_len = (uint32_t)ct_len; /* plaintext size equals ciphertext size */

    if (*out_len < ct_len)
        return TEE_ERROR_SHORT_BUFFER;

    /* Prepare transient key object */
    res = TEE_AllocateTransientObject(TEE_TYPE_AES, KEK_BITS, &key);
    if (res)
        goto out;
    TEE_Attribute attr;
    TEE_InitRefAttribute(&attr, TEE_ATTR_SECRET_VALUE, kek, kek_len);
    res = TEE_PopulateTransientObject(key, &attr, 1);
    if (res)
        goto out;

    /* Allocate operation */
    res = TEE_AllocateOperation(&op, TEE_ALG_AES_GCM, TEE_MODE_DECRYPT, KEK_BITS);
    if (res)
        goto out;
    res = TEE_SetOperationKey(op, key);
    if (res)
        goto out;

    TEE_AEInit(op, iv, 12, /*tagLen*/ 128, /*aadLen*/ 0, /*payloadLen*/ (uint32_t)ct_len);

    res = TEE_AEDecryptFinal(op,
                             (void *)ct, (uint32_t)ct_len,
                             out_buf, &dst_len,
                             (void *)tag, (uint32_t)16);
    if (res == TEE_SUCCESS)
        *out_len = dst_len;

out:
    if (op)
        TEE_FreeOperation(op);
    if (key)
        TEE_FreeTransientObject(key);
    return res;
}

/* ===== Self-test ===== */

static TEE_Result self_test(void *io_buf, uint32_t *io_len32)
{
    static const uint8_t kTestPlain[] = {
        0x54, 0x45, 0x53, 0x54, /* "TEST" */
        0x00, 0x11, 0x22, 0x33, 0x44,
        0x55, 0x66, 0x77, 0x88, 0x99};
    const size_t pt_len = sizeof(kTestPlain);

    uint8_t kek[KEK_BITS / 8];
    TEE_Result res = get_or_create_kek(kek, sizeof(kek));
    if (res)
        goto fail;

    size_t ct_len = pt_len + 12 + 16;
    uint8_t *ct = TEE_Malloc(ct_len, 0);
    if (!ct)
    {
        res = TEE_ERROR_OUT_OF_MEMORY;
        goto fail;
    }

    res = aes_gcm_encrypt(kek, sizeof(kek), kTestPlain, pt_len, ct, &ct_len);
    if (res)
    {
        TEE_Free(ct);
        goto fail;
    }

    size_t dec_len = pt_len;
    uint8_t *dec = TEE_Malloc(dec_len, 0);
    if (!dec)
    {
        TEE_Free(ct);
        res = TEE_ERROR_OUT_OF_MEMORY;
        goto fail;
    }

    res = aes_gcm_decrypt(kek, sizeof(kek), ct, ct_len, dec, &dec_len);
    TEE_Free(ct);
    if (res)
    {
        TEE_Free(dec);
        goto fail;
    }

    if (dec_len != pt_len || TEE_MemCompare(dec, kTestPlain, pt_len) != 0)
    {
        TEE_Free(dec);
        res = TEE_ERROR_GENERIC;
        goto fail;
    }
    TEE_Free(dec);

    {
        const char *ok = "CMD_TEST: OK (KEK present, AES-GCM round-trip verified)";
        size_t need = strlen(ok) + 1;
        if (*io_len32 >= need)
        {
            TEE_MemMove(io_buf, ok, need);
            *io_len32 = need;
        }
        else if (*io_len32 > 0)
        {
            TEE_MemMove(io_buf, ok, *io_len32 - 1);
            ((char *)io_buf)[*io_len32 - 1] = '\0';
        }
    }
    return TEE_SUCCESS;

fail:
{
    const char *err = "CMD_TEST: FAIL";
    size_t need = strlen(err) + 1;
    if (*io_len32 >= need)
    {
        TEE_MemMove(io_buf, err, need);
        *io_len32 = need;
    }
    else if (*io_len32 > 0)
    {
        TEE_MemMove(io_buf, err, *io_len32 - 1);
        ((char *)io_buf)[*io_len32 - 1] = '\0';
    }
}
    return res;
}

/* ===== TA entry points ===== */

TEE_Result TA_CreateEntryPoint(void) { return TEE_SUCCESS; }
void TA_DestroyEntryPoint(void) {}

TEE_Result TA_OpenSessionEntryPoint(uint32_t param_types,
                                    TEE_Param params[4],
                                    void **sess_ctx)
{
    (void)param_types;
    (void)params;
    (void)sess_ctx;
    return TEE_SUCCESS;
}

void TA_CloseSessionEntryPoint(void *sess_ctx) { (void)sess_ctx; }

/* Dispatcher */
TEE_Result TA_InvokeCommandEntryPoint(void *sess_ctx, uint32_t cmd_id,
                                      uint32_t param_types, TEE_Param params[4])
{
    (void)sess_ctx;

    /* All commands use a single INOUT memref for simplicity */
    const uint32_t exp = TEE_PARAM_TYPES(TEE_PARAM_TYPE_MEMREF_INOUT,
                                         TEE_PARAM_TYPE_NONE,
                                         TEE_PARAM_TYPE_NONE,
                                         TEE_PARAM_TYPE_NONE);

    if (param_types != exp)
        return TEE_ERROR_BAD_PARAMETERS;

    if (cmd_id == CMD_TEST)
    {
        return self_test(params[0].memref.buffer, &params[0].memref.size);
    }

    /* Wrap / Unwrap require the KEK */
    uint8_t kek[KEK_BITS / 8];
    TEE_Result res = get_or_create_kek(kek, sizeof(kek));
    if (res)
        return res;

    void *buf = params[0].memref.buffer;
    size_t len = params[0].memref.size;

    if (cmd_id == CMD_WRAP)
    {
        size_t out_len = len + 12 + 16;
        void *tmp = TEE_Malloc(out_len, 0);
        if (!tmp)
            return TEE_ERROR_OUT_OF_MEMORY;

        res = aes_gcm_encrypt(kek, sizeof(kek), buf, len, tmp, &out_len);
        if (res == TEE_SUCCESS)
        {
            if (out_len <= params[0].memref.size)
            {
                TEE_MemMove(buf, tmp, out_len);
                params[0].memref.size = out_len;
            }
            else
            {
                res = TEE_ERROR_SHORT_BUFFER;
            }
        }
        TEE_Free(tmp);
        return res;
    }
    else if (cmd_id == CMD_UNWRAP)
    {
        size_t out_len = len; /* plaintext equals ct size */
        void *tmp = TEE_Malloc(out_len, 0);
        if (!tmp)
            return TEE_ERROR_OUT_OF_MEMORY;

        res = aes_gcm_decrypt(kek, sizeof(kek), buf, len, tmp, &out_len);
        if (res == TEE_SUCCESS)
        {
            if (out_len <= params[0].memref.size)
            {
                TEE_MemMove(buf, tmp, out_len);
                params[0].memref.size = out_len;
            }
            else
            {
                res = TEE_ERROR_SHORT_BUFFER;
            }
        }
        TEE_Free(tmp);
        return res;
    }

    return TEE_ERROR_NOT_SUPPORTED;
}

/* ===== TA properties (optional when using user_ta_header.c template) =====
 * If you generate your TA from the standard OP-TEE templates, the TA UUID
 * and props are typically defined in user_ta_header.c produced by the devkit.
 * If you embed here, you would define TA_UUID and compile accordingly.
 */
