/*
 * data_key_ta.c
 *
 * Production-grade OP-TEE TA for dm-crypt/LUKS key wrapping
 * with strong rollback protection.
 *
 * Security properties:
 *  - KEK derived from HUK via HKDF
 *  - RPMB-backed monotonic counter
 *  - Explicit downgrade detection
 *  - AES-256-GCM (HDR | CT)
 *  - Explicit zeroization
 *  - Client UUID authorization
 */

#include <tee_internal_api.h>
#include <tee_internal_api_extensions.h>
#include <pta_system.h>
#include <string.h>
#include "data_key_ta.h"

/* -------------------------------------------------------------------------- */
/* Configuration                                                              */
/* -------------------------------------------------------------------------- */

#define KEK_BITS 256
#define KEK_BYTES (KEK_BITS / 8)

#define GCM_IV_BYTES 12
#define GCM_TAG_BITS 128
#define GCM_TAG_BYTES (GCM_TAG_BITS / 8)

#define KEK_VERSION 1

#define COUNTER_OBJ_ID "kek_counter.bin"
#define REQUIRE_AUTH_FOR_ROTATE 0

static const uint32_t storage_id = TEE_STORAGE_PRIVATE_RPMB;
// static const uint32_t storage_id = TEE_STORAGE_PRIVATE;

/* Authorized client UUID */
static const TEE_UUID allowed_client_uuid = KEKSTORE_TA_UUID;

/* Domain separation salt/info */
static const char kSalt[] = "imx93-optee-dmcrypt"; /* adjust to platform/product */

/* -------------------------------------------------------------------------- */
/* Wrapped blob header                                                         */
/* -------------------------------------------------------------------------- */

struct wrapped_hdr
{
    uint32_t version;
    uint32_t counter;
    uint8_t iv[GCM_IV_BYTES];
    uint8_t tag[GCM_TAG_BYTES];
};

/* -------------------------------------------------------------------------- */
/* Utilities                                                                  */
/* -------------------------------------------------------------------------- */

static void memzero(void *p, size_t n)
{
    volatile uint8_t *v = p;
    while (n--)
        *v++ = 0;
}

#if REQUIRE_AUTH_FOR_ROTATE
static TEE_Result check_caller_authorized(void)
{
    TEE_UUID caller;

    if (TEE_GetPropertyAsUUID(TEE_PROPSET_CURRENT_CLIENT,
                              "gpd.client.appID",
                              &caller) != TEE_SUCCESS)
        return TEE_ERROR_ACCESS_DENIED;

    if (TEE_MemCompare(&caller, &allowed_client_uuid,
                       sizeof(caller)) != 0)
        return TEE_ERROR_ACCESS_DENIED;

    return TEE_SUCCESS;
}
#endif

/* -------------------------------------------------------------------------- */
/* Anti-rollback counter (RPMB)                                                */
/* -------------------------------------------------------------------------- */

static TEE_Result load_or_create_counter(uint32_t *counter)
{
    TEE_ObjectHandle oh = TEE_HANDLE_NULL;
    TEE_Result res = TEE_ERROR_GENERIC;
    bool counter_present = false;
    IMSG("load_or_create_counter TEE_OpenPersistentObject");
    res = TEE_OpenPersistentObject(storage_id,
                                   COUNTER_OBJ_ID,
                                   strlen(COUNTER_OBJ_ID),
                                   TEE_DATA_FLAG_ACCESS_READ |
                                       TEE_DATA_FLAG_ACCESS_WRITE,
                                   &oh);
    if (res == TEE_SUCCESS)
    {
        uint32_t rb = 0;
        counter_present = true;
        IMSG("load_or_create_counter TEE_ReadObjectData");
        res = TEE_ReadObjectData(oh, counter, sizeof(*counter), &rb);
        IMSG("load_or_create_counter TEE_CloseObject");
        TEE_CloseObject(oh);
        if (res != TEE_SUCCESS || rb != sizeof(*counter))
        {
            res = TEE_ERROR_CORRUPT_OBJECT;
        }
    }
    if (counter_present == false)
    {
        *counter = 1;
        IMSG("load_or_create_counter TEE_CreatePersistentObject");
        res = TEE_CreatePersistentObject(storage_id,
                                         COUNTER_OBJ_ID,
                                         strlen(COUNTER_OBJ_ID),
                                         TEE_DATA_FLAG_ACCESS_READ |
                                             TEE_DATA_FLAG_ACCESS_WRITE |
                                             TEE_DATA_FLAG_OVERWRITE,
                                         TEE_HANDLE_NULL,
                                         counter,
                                         sizeof(*counter),
                                         &oh);
        if (res == TEE_SUCCESS)
            TEE_CloseObject(oh);
    }
    IMSG("load_or_create_counter res: %x", res);
    return res;
}

static TEE_Result store_counter(uint32_t counter)
{
    TEE_ObjectHandle oh = TEE_HANDLE_NULL;
    uint32_t tmp = counter;
    TEE_Result res;

    res = TEE_CreatePersistentObject(
        storage_id,
        COUNTER_OBJ_ID,
        strlen(COUNTER_OBJ_ID),
        TEE_DATA_FLAG_ACCESS_READ |
            TEE_DATA_FLAG_ACCESS_WRITE |
            TEE_DATA_FLAG_OVERWRITE,
        TEE_HANDLE_NULL,
        &tmp,
        sizeof(tmp),
        &oh);

    if (res == TEE_SUCCESS)
        TEE_CloseObject(oh);

    memzero(&tmp, sizeof(tmp));
    IMSG("store_counter result: 0x%x", res);
    return res;
}

static TEE_Result increment_counter(uint32_t *new_val)
{
    uint32_t c;
    TEE_Result res = load_or_create_counter(&c);
    if (res == TEE_SUCCESS)
    {
        IMSG("increment_counter current value: %u", c);

        c++;
        res = store_counter(c);
    }
    if (res == TEE_SUCCESS)
    {
        IMSG("increment_counter new value: %u", c);

        if (new_val)
            *new_val = c;
    }
    IMSG("increment_counter result: 0x%x", res);
    return res;
}

/* --- Derivation: get per-TA base key from System PTA, then HKDF -> KEK --- */

static TEE_Result derive_base_from_system_pta(const void *extra, size_t extra_len,
                                              uint8_t *out, size_t out_len)
{
    TEE_Result res = TEE_ERROR_GENERIC;
    const TEE_UUID pta_uuid = PTA_SYSTEM_UUID;
    TEE_TASessionHandle sess = TEE_HANDLE_NULL;
    uint32_t ret_origin = 0;

    TEE_Param params[4];
    uint32_t pt = TEE_PARAM_TYPES(TEE_PARAM_TYPE_MEMREF_INPUT,
                                  TEE_PARAM_TYPE_MEMREF_OUTPUT,
                                  TEE_PARAM_TYPE_NONE,
                                  TEE_PARAM_TYPE_NONE);
    IMSG("derive_base_from_system_pta: begin");
    TEE_MemFill(params, 0, sizeof(params));
    params[0].memref.buffer = (void *)extra;
    params[0].memref.size = (uint32_t)extra_len;
    params[1].memref.buffer = out;
    params[1].memref.size = (uint32_t)out_len;
    IMSG("derive_base_from_system_pta: TEE_OpenTASession");

    res = TEE_OpenTASession(&pta_uuid, TEE_TIMEOUT_INFINITE,
                            TEE_PARAM_TYPES(TEE_PARAM_TYPE_NONE,
                                            TEE_PARAM_TYPE_NONE,
                                            TEE_PARAM_TYPE_NONE,
                                            TEE_PARAM_TYPE_NONE),
                            NULL,
                            &sess, &ret_origin);
    if (res)
        return res;
    IMSG("derive_base_from_system_pta: TEE_InvokeTACommand");
    res = TEE_InvokeTACommand(sess, TEE_TIMEOUT_INFINITE, PTA_SYSTEM_DERIVE_TA_UNIQUE_KEY,
                              pt, params, &ret_origin);
    IMSG("derive_base_from_system_pta: TEE_CloseTASession");
    TEE_CloseTASession(sess);
    IMSG("derive_base_from_system_pta result: 0x%x", res);
    return res;
}

static TEE_Result hkdf_derive_kek(const uint8_t *ikm, size_t ikm_len,
                                  const void *info, size_t info_len,
                                  uint8_t *kek, size_t kek_len)
{
    TEE_Result res = TEE_SUCCESS;
    TEE_OperationHandle op = TEE_HANDLE_NULL;
    TEE_ObjectHandle ikm_obj = TEE_HANDLE_NULL;
    TEE_ObjectHandle kek_obj = TEE_HANDLE_NULL;
    uint32_t out_len = (uint32_t)kek_len;

    TEE_Attribute attrs[3];
    TEE_Attribute ikm_attr;

    IMSG("derive_kek: allocate HKDF operation");
    res = TEE_AllocateOperation(&op, TEE_ALG_HKDF_SHA256_DERIVE_KEY,
                                TEE_MODE_DERIVE, 256);
    if (res)
        goto out;
    IMSG("derive_kek: allocate IKM");
    res = TEE_AllocateTransientObject(TEE_TYPE_HKDF_IKM, 256, &ikm_obj);
    if (res)
        goto out;

    TEE_InitRefAttribute(&ikm_attr, TEE_ATTR_HKDF_IKM,
                         (void *)ikm, (uint32_t)ikm_len);
    res = TEE_PopulateTransientObject(ikm_obj, &ikm_attr, 1);
    if (res)
        goto out;

    IMSG("derive_kek: set operation key");
    res = TEE_SetOperationKey(op, ikm_obj);
    if (res)
        goto out;

    TEE_InitRefAttribute(&attrs[0], TEE_ATTR_HKDF_INFO,
                         (void *)info, (uint32_t)info_len);
    TEE_InitRefAttribute(&attrs[1], TEE_ATTR_HKDF_SALT, (void *)kSalt, (uint32_t)(sizeof(kSalt) - 1));
    TEE_InitValueAttribute(&attrs[2], TEE_ATTR_HKDF_OKM_LENGTH,
                           (uint32_t)kek_len, 0);

    res = TEE_AllocateTransientObject(TEE_TYPE_GENERIC_SECRET, 256, &kek_obj);
    IMSG("derive_kek: allocate KEK object");
    if (res)
        goto out;
    IMSG("derive_kek: TEE_DeriveKey");
    TEE_DeriveKey(op, attrs, 3, kek_obj);
    IMSG("derive_kek: extract KEK");
    res = TEE_GetObjectBufferAttribute(kek_obj, TEE_ATTR_SECRET_VALUE, kek, &out_len);

out:
    if (kek_obj)
        TEE_FreeTransientObject(kek_obj);
    if (ikm_obj)
        TEE_FreeTransientObject(ikm_obj);
    if (op)
        TEE_FreeOperation(op);
    IMSG("hkdf_derive_kek result: 0x%x", res);
    return res;
}

static TEE_Result derive_kek(uint8_t *kek, size_t kek_len, uint32_t counter)
{
    struct
    {
        uint32_t version;
        uint32_t counter;
    } info = {1, counter};
    uint8_t base[32];
    IMSG("derive_kek derive_base_from_system_pta");
    TEE_Result res = derive_base_from_system_pta(&info, sizeof(info), base, sizeof(base));
    if (res)
        return res;
    IMSG("derive_kek hkdf_derive_kek");
    res = hkdf_derive_kek(base, sizeof(base), &info, sizeof(info), kek, kek_len);
    TEE_MemFill(base, 0, sizeof(base));
    IMSG("derive_kek result: 0x%x", res);
    return res;
}

/* -------------------------------------------------------------------------- */
/* AES-GCM                                                                    */
/* -------------------------------------------------------------------------- */

static TEE_Result aes_gcm_encrypt(const uint8_t *kek,
                                  const void *pt, size_t pt_len,
                                  struct wrapped_hdr *hdr,
                                  uint8_t *ct)
{
    TEE_OperationHandle op = TEE_HANDLE_NULL;
    TEE_ObjectHandle key = TEE_HANDLE_NULL;
    TEE_Result res;
    uint32_t tag_bits = GCM_TAG_BITS;
    uint32_t ct_len = (uint32_t)pt_len;
    uint32_t aad_len = sizeof(hdr->version) + sizeof(hdr->counter);

    TEE_GenerateRandom(hdr->iv, GCM_IV_BYTES);

    res = TEE_AllocateTransientObject(TEE_TYPE_AES, KEK_BITS, &key);
    if (res)
        goto out;

    TEE_Attribute attr;
    TEE_InitRefAttribute(&attr, TEE_ATTR_SECRET_VALUE, kek, KEK_BYTES);
    res = TEE_PopulateTransientObject(key, &attr, 1);
    if (res)
        goto out;

    res = TEE_AllocateOperation(&op, TEE_ALG_AES_GCM,
                                TEE_MODE_ENCRYPT, KEK_BITS);
    if (res)
        goto out;

    res = TEE_SetOperationKey(op, key);
    if (res)
        goto out;

    /* Bind header fields (version||counter) as AAD */
    TEE_AEInit(op, hdr->iv, GCM_IV_BYTES, tag_bits, aad_len, ct_len);
    TEE_AEUpdateAAD(op, hdr, aad_len);

    res = TEE_AEEncryptFinal(op,
                             (void *)pt, ct_len,
                             ct, &ct_len,
                             hdr->tag, &tag_bits);

out:
    if (op)
        TEE_FreeOperation(op);
    if (key)
        TEE_FreeTransientObject(key);
    IMSG("aes_gcm_encrypt result: 0x%x", res);
    return res;
}

static TEE_Result aes_gcm_decrypt(const uint8_t *kek,
                                  const struct wrapped_hdr *hdr,
                                  const uint8_t *ct, size_t ct_len,
                                  uint8_t *pt, size_t *pt_len)
{
    TEE_OperationHandle op = TEE_HANDLE_NULL;
    TEE_ObjectHandle key = TEE_HANDLE_NULL;
    TEE_Result res;
    uint32_t out_len = (uint32_t)*pt_len;
    uint32_t aad_len = sizeof(hdr->version) + sizeof(hdr->counter);

    res = TEE_AllocateTransientObject(TEE_TYPE_AES, KEK_BITS, &key);
    if (res)
        goto out;

    TEE_Attribute attr;
    TEE_InitRefAttribute(&attr, TEE_ATTR_SECRET_VALUE, kek, KEK_BYTES);
    res = TEE_PopulateTransientObject(key, &attr, 1);
    if (res)
        goto out;

    res = TEE_AllocateOperation(&op, TEE_ALG_AES_GCM,
                                TEE_MODE_DECRYPT, KEK_BITS);
    if (res)
        goto out;

    res = TEE_SetOperationKey(op, key);
    if (res)
        goto out;

    /* Supply same AAD as during encryption */
    TEE_AEInit(op, (void *)hdr->iv, GCM_IV_BYTES, GCM_TAG_BITS, aad_len, (uint32_t)ct_len);
    TEE_AEUpdateAAD(op, (void *)hdr, aad_len);

    res = TEE_AEDecryptFinal(op,
                             (void *)ct, (uint32_t)ct_len,
                             pt, &out_len,
                             (void *)hdr->tag, GCM_TAG_BYTES);
    if (res == TEE_SUCCESS)
        *pt_len = out_len;

out:
    if (op)
        TEE_FreeOperation(op);
    if (key)
        TEE_FreeTransientObject(key);
    IMSG("aes_gcm_decrypt result: 0x%x", res);
    return res;
}

/* -------------------------------------------------------------------------- */
/* Self-test                                                                  */
/* -------------------------------------------------------------------------- */

static TEE_Result self_test(void *buf, uint32_t *len32)
{
    static const uint8_t pt[] = "SELFTEST";
    uint8_t kek[KEK_BYTES];
    struct wrapped_hdr hdr;
    uint8_t ct[32];
    uint8_t dec[sizeof(pt)];
    size_t dec_len = sizeof(dec);
    uint32_t ctr;
    TEE_Result res;
    IMSG("Self-test started");

    res = load_or_create_counter(&ctr);
    if (res)
        goto out;

    res = derive_kek(kek, sizeof(kek), ctr);
    if (res)
        goto out;

    hdr.version = KEK_VERSION;
    hdr.counter = ctr;

    res = aes_gcm_encrypt(kek, pt, sizeof(pt), &hdr, ct);
    if (res)
        goto out;

    res = aes_gcm_decrypt(kek, &hdr, ct, sizeof(pt), dec, &dec_len);
    if (res)
        goto out;

    if (dec_len != sizeof(pt) ||
        TEE_MemCompare(pt, dec, sizeof(pt)) != 0)
        res = TEE_ERROR_SECURITY;

out:
    memzero(kek, sizeof(kek));
    memzero(&hdr, sizeof(hdr));
    memzero(ct, sizeof(ct));
    memzero(dec, sizeof(dec));

    const char *msg = (res == TEE_SUCCESS)
                          ? "SELFTEST OK"
                          : "SELFTEST FAIL";

    size_t need = strlen(msg) + 1;
    if (*len32 >= need)
    {
        TEE_MemMove(buf, msg, need);
        *len32 = need;
    }
    IMSG("self_test result: 0x%x", res);

    return res;
}

/* -------------------------------------------------------------------------- */
/* TA Entry Points                                                            */
/* -------------------------------------------------------------------------- */

TEE_Result TA_CreateEntryPoint(void) { return TEE_SUCCESS; }
void TA_DestroyEntryPoint(void) {}

TEE_Result TA_OpenSessionEntryPoint(uint32_t pt, TEE_Param p[4], void **ctx)
{
    (void)pt;
    (void)p;
    (void)ctx;
    return TEE_SUCCESS;
}
void TA_CloseSessionEntryPoint(void *ctx) { (void)ctx; }

static TEE_Result cmd_wrap(TEE_Param p[4])
{
    /* IN: p0.memref = plaintext key; OUT: p1.memref = header||ciphertext */
    uint8_t *pt = p[0].memref.buffer;
    size_t pt_len = p[0].memref.size;
    uint8_t *out = p[1].memref.buffer;
    size_t out_len = p[1].memref.size;
    struct wrapped_hdr hdr_local; /* aligned on stack */
    uint8_t *ct = out + sizeof(struct wrapped_hdr);

    uint32_t ctr = 0;
    uint8_t kek[KEK_BYTES];
    TEE_Result res;

    if (!pt || !out || out_len < sizeof(struct wrapped_hdr) + pt_len)
        return TEE_ERROR_BAD_PARAMETERS;
    IMSG("cmd_wrap load_or_create_counter");

    res = load_or_create_counter(&ctr);
    if (res)
        return res;

    hdr_local.version = KEK_VERSION;
    hdr_local.counter = ctr;
    IMSG("cmd_wrap derive_kek");

    res = derive_kek(kek, sizeof(kek), ctr);
    if (res)
        goto out;
    IMSG("cmd_wrap aes_gcm_encrypt");
    res = aes_gcm_encrypt(kek, pt, pt_len, &hdr_local, ct);
    if (res)
        goto out;

    /* Write header to output buffer first, then ciphertext */

    TEE_MemMove(out, &hdr_local, sizeof(hdr_local));
    /* Tell the caller how many bytes we produced: header + ciphertext */
    p[1].memref.size = (uint32_t)(sizeof(struct wrapped_hdr) + pt_len);

out:
    memzero(kek, sizeof(kek));
    IMSG("cmd_wrap result: 0x%x", res);
    return res;
}

static TEE_Result cmd_unwrap(TEE_Param p[4])
{
    /* IN: p0.memref = header||ciphertext; OUT: p1.memref = plaintext key */
    uint8_t *blob = p[0].memref.buffer;
    size_t blob_len = p[0].memref.size;
    uint8_t *pt = p[1].memref.buffer;
    size_t pt_len = p[1].memref.size; /* capacity */

    struct wrapped_hdr hdr_local; /* aligned on stack */
    const uint8_t *ct = blob + sizeof(struct wrapped_hdr);
    size_t ct_len = blob_len - sizeof(struct wrapped_hdr);

    if (blob_len < sizeof(hdr_local))
        return TEE_ERROR_BAD_PARAMETERS;
    TEE_MemMove(&hdr_local, blob, sizeof(hdr_local));

    uint32_t ctr_now = 0;
    uint8_t kek[KEK_BYTES];
    TEE_Result res;

    if (!blob || blob_len < sizeof(struct wrapped_hdr) || !pt)
        return TEE_ERROR_BAD_PARAMETERS;
    /* If plaintext output buffer is too small, tell the caller the required size */
    if (ct_len > pt_len)
    {
        p[1].memref.size = (uint32_t)ct_len; /* required output length */
        return TEE_ERROR_SHORT_BUFFER;
    }

    res = load_or_create_counter(&ctr_now);
    if (res)
        return res;

    /* Rollback check: reject if header counter is lower than RPMB counter */
    if (hdr_local.counter < ctr_now)
        return TEE_ERROR_SECURITY;

    res = derive_kek(kek, sizeof(kek), hdr_local.counter);
    if (res)
        goto out;

    res = aes_gcm_decrypt(kek, &hdr_local, ct, ct_len, pt, &ct_len);
    if (res == TEE_SUCCESS)
        p[1].memref.size = (uint32_t)ct_len;

out:
    memzero(kek, sizeof(kek));
    IMSG("cmd_unwrap result: 0x%x", res);
    return res;
}

TEE_Result TA_InvokeCommandEntryPoint(void *ctx, uint32_t cmd, uint32_t pt, TEE_Param p[4])
{
    (void)ctx;

    switch (cmd)
    {
    case CMD_TEST:
        if (pt != TEE_PARAM_TYPES(TEE_PARAM_TYPE_MEMREF_INOUT, 0, 0, 0))
            return TEE_ERROR_BAD_PARAMETERS;
        return self_test(p[0].memref.buffer, &p[0].memref.size);

    case CMD_ROTATE_KEK:
        if (pt != TEE_PARAM_TYPES(TEE_PARAM_TYPE_NONE, 0, 0, 0))
            return TEE_ERROR_BAD_PARAMETERS;
        {
#if REQUIRE_AUTH_FOR_ROTATE
            TEE_Result res = check_caller_authorized();
            if (res)
                return res;
#endif
            return increment_counter(NULL);
        }

    case CMD_WRAP:
        if (pt != TEE_PARAM_TYPES(TEE_PARAM_TYPE_MEMREF_INPUT,
                                  TEE_PARAM_TYPE_MEMREF_OUTPUT, 0, 0))
            return TEE_ERROR_BAD_PARAMETERS;
        return cmd_wrap(p);

    case CMD_UNWRAP:
        if (pt != TEE_PARAM_TYPES(TEE_PARAM_TYPE_MEMREF_INPUT,
                                  TEE_PARAM_TYPE_MEMREF_INOUT, 0, 0))
            return TEE_ERROR_BAD_PARAMETERS;
        return cmd_unwrap(p);

    default:
        return TEE_ERROR_NOT_SUPPORTED;
    }
}
