
/*
 * optee_get_key.c
 *
 * Host client for OP-TEE TA: test / wrap / unwrap / rotate dm-crypt keys
 * plus regress tests.
 *
 * License: BSD-2-Clause
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <getopt.h>
#include <errno.h>
#include <time.h>

#include <tee_client_api.h>
#include "data_key_ta.h"

/* ---------------- TEEC helpers ---------------- */
static TEEC_Result open_ta(TEEC_Context *ctx, TEEC_Session *sess)
{
    TEEC_UUID uuid = KEKSTORE_TA_UUID;
    uint32_t origin = 0;
    TEEC_Result res;

    res = TEEC_InitializeContext(NULL, ctx);
    if (res)
        return res;

    res = TEEC_OpenSession(ctx, sess, &uuid,
                           TEEC_LOGIN_PUBLIC, NULL, NULL, &origin);
    if (res)
    {
        TEEC_FinalizeContext(ctx);
    }
    return res;
}

static void close_ta(TEEC_Context *ctx, TEEC_Session *sess)
{
    TEEC_CloseSession(sess);
    TEEC_FinalizeContext(ctx);
}

/* SELFTEST (CMD_TEST) uses single MEMREF_INOUT (your TA’s API) */
static TEEC_Result run_selftest(char *outbuf, size_t *inout_len)
{
    TEEC_Context ctx;
    TEEC_Session sess;
    TEEC_Operation op;
    uint32_t origin = 0;
    TEEC_Result res;

    res = open_ta(&ctx, &sess);
    if (res)
    {
        fprintf(stderr, "Open TA failed: 0x%x\n", res);
        return res;
    }
    memset(&op, 0, sizeof(op));
    op.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_TEMP_INOUT, TEEC_NONE, TEEC_NONE, TEEC_NONE);
    op.params[0].tmpref.buffer = outbuf;
    op.params[0].tmpref.size = *inout_len;

    res = TEEC_InvokeCommand(&sess, CMD_TEST, &op, &origin);
    if (res == TEEC_SUCCESS)
        *inout_len = op.params[0].tmpref.size;

    close_ta(&ctx, &sess);
    return res;
}

/* ROTATE (CMD_ROTATE_KEK) uses NONE (your TA’s API) */
static TEEC_Result do_rotate(void)
{
    TEEC_Context ctx;
    TEEC_Session sess;
    TEEC_Operation op;
    uint32_t origin = 0;
    TEEC_Result res;

    res = open_ta(&ctx, &sess);
    if (res)
    {
        fprintf(stderr, "Open TA failed: 0x%x\n", res);
        return res;
    }
    memset(&op, 0, sizeof(op));
    op.paramTypes = TEEC_PARAM_TYPES(TEEC_NONE, TEEC_NONE, TEEC_NONE, TEEC_NONE);
    res = TEEC_InvokeCommand(&sess, CMD_ROTATE_KEK, &op, &origin);

    close_ta(&ctx, &sess);
    return res;
}

/* WRAP (CMD_WRAP) uses: p0=INPUT(pt), p1=OUTPUT(blob) */
static TEEC_Result do_wrap(const uint8_t *pt, size_t pt_len,
                           uint8_t *blob, size_t *blob_len)
{
    TEEC_Context ctx;
    TEEC_Session sess;
    TEEC_Operation op;
    uint32_t origin = 0;
    TEEC_Result res;

    res = open_ta(&ctx, &sess);
    if (res)
        return res;

    memset(&op, 0, sizeof(op));
    op.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_TEMP_INPUT,
                                     TEEC_MEMREF_TEMP_OUTPUT,
                                     TEEC_NONE, TEEC_NONE);
    op.params[0].tmpref.buffer = (void *)pt;
    op.params[0].tmpref.size = pt_len;
    op.params[1].tmpref.buffer = blob;
    op.params[1].tmpref.size = *blob_len;

    res = TEEC_InvokeCommand(&sess, CMD_WRAP, &op, &origin);
    if (res == TEEC_SUCCESS)
        *blob_len = op.params[1].tmpref.size;

    close_ta(&ctx, &sess);
    return res;
}

/* UNWRAP (CMD_UNWRAP) uses: p0=INPUT(blob), p1=INOUT(pt) */
static TEEC_Result do_unwrap(const uint8_t *blob, size_t blob_len,
                             uint8_t *pt, size_t *pt_len)
{
    TEEC_Context ctx;
    TEEC_Session sess;
    TEEC_Operation op;
    uint32_t origin = 0;
    TEEC_Result res;

    res = open_ta(&ctx, &sess);
    if (res)
        return res;

    memset(&op, 0, sizeof(op));
    op.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_TEMP_INPUT,
                                     TEEC_MEMREF_TEMP_INOUT,
                                     TEEC_NONE, TEEC_NONE);
    op.params[0].tmpref.buffer = (void *)blob;
    op.params[0].tmpref.size = blob_len;
    op.params[1].tmpref.buffer = pt;
    op.params[1].tmpref.size = *pt_len; /* capacity in; TA sets to out size */

    res = TEEC_InvokeCommand(&sess, CMD_UNWRAP, &op, &origin);
    if (res == TEEC_SUCCESS)
        *pt_len = op.params[1].tmpref.size;

    close_ta(&ctx, &sess);
    return res;
}

/* ---------------- File helpers (as you had) ---------------- */
static int read_file(const char *path, uint8_t **buf, size_t *len)
{
    FILE *f = fopen(path, "rb");
    if (!f)
    {
        perror("fopen");
        return -1;
    }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    rewind(f);
    if (sz <= 0)
    {
        fclose(f);
        return -1;
    }
    *buf = malloc((size_t)sz);
    if (!*buf)
    {
        fclose(f);
        return -1;
    }
    if (fread(*buf, 1, (size_t)sz, f) != (size_t)sz)
    {
        fclose(f);
        free(*buf);
        return -1;
    }
    fclose(f);
    *len = (size_t)sz;
    return 0;
}
static int write_file(const char *path, const uint8_t *buf, size_t len)
{
    FILE *f = fopen(path, "wb");
    if (!f)
    {
        perror("fopen");
        return -1;
    }
    if (fwrite(buf, 1, len, f) != len)
    {
        fclose(f);
        return -1;
    }
    fclose(f);
    return 0;
}

/* ---------------- CLI & regression ---------------- */
static void usage(const char *prog)
{
    fprintf(stderr,
            "Usage:\n"
            " %s --test\n"
            " %s --wrap   --in <plain.bin>   --out <wrapped.bin> # 'head -c 32 /dev/urandom > plain.bin' 'optee_get_key --wrap --in plain.bin --out wrapped.bin'\n"
            " %s --unwrap --in <wrapped.bin> --out <plain.bin> # 'optee_get_key --unwrap --in wrapped.bin --out plain_out.bin' 'cmp plain.bin plain_out.bin && echo \"Match\"'\n"
            " %s --rotate\n"
            " %s --regress        (wrap+unwrap in-memory, verify)\n"
            " %s --regress-rotate (wrap, rotate; unwrap must fail)\n",
            prog, prog, prog, prog, prog, prog);
}

/* Regress: wrap -> unwrap -> rotate -> unwrap(fail) */
static int cmd_regress(void)
{
    /* 32-byte random key */
    uint8_t pt[32], unwrapped[32];
    uint8_t blob[512]; /* plenty for header+ct */
    size_t blob_len = sizeof(blob), unwrapped_len = sizeof(unwrapped);
    TEEC_Result r;

    /* Not cryptographically strong; good enough for test */
    srand((unsigned)time(NULL));
    for (size_t i = 0; i < sizeof(pt); i++)
        pt[i] = rand() & 0xFF;

    r = do_wrap(pt, sizeof(pt), blob, &blob_len);
    if (r)
    {
        fprintf(stderr, "WRAP failed: 0x%x\n", r);
        return 2;
    }
    printf("WRAP ok: blob=%zu bytes\n", blob_len);

    /* Ensure output capacity >= ciphertext length (blob_len - header) */
    const size_t hdr_len = 4 + 4 + 12 + 16; /* version + counter + IV + tag = 36 */
    if (blob_len < hdr_len)
    {
        fprintf(stderr, "regress: invalid blob length (%zu < %zu)\n", blob_len, hdr_len);
        return 3;
    }
    const size_t ct_len = blob_len - hdr_len;
    if (ct_len > sizeof(unwrapped))
    {
        fprintf(stderr, "regress: output buffer too small (%zu < %zu)\n",
                sizeof(unwrapped), ct_len);
        return TEEC_ERROR_SHORT_BUFFER;
    }

    unwrapped_len = sizeof(unwrapped); /* capacity */
    r = do_unwrap(blob, blob_len, unwrapped, &unwrapped_len);
    if (r)
    {
        fprintf(stderr, "UNWRAP failed: 0x%x\n", r);
        return 3;
    }
    if (unwrapped_len != sizeof(pt) || memcmp(pt, unwrapped, sizeof(pt)))
    {
        fprintf(stderr, "regress: mismatch\n");
        return 4;
    }

    printf("regress: OK (wrapped %zuB -> %zuB and unwrapped identically)\n",
           sizeof(pt), blob_len);

    return 0;
}

/* Regress + rotation: unwrap must fail after rotate */
static int cmd_regress_rotate(void)
{
    uint8_t pt[32], unwrapped[32];
    uint8_t blob[512];
    size_t blob_len = sizeof(blob), unwrapped_len = sizeof(unwrapped);
    TEEC_Result r;

    srand((unsigned)time(NULL));
    for (size_t i = 0; i < sizeof(pt); i++)
        pt[i] = rand() & 0xFF;

    r = do_wrap(pt, sizeof(pt), blob, &blob_len);
    if (r)
    {
        fprintf(stderr, "WRAP failed: 0x%x\n", r);
        return 2;
    }

    r = do_rotate();
    if (r)
    {
        fprintf(stderr, "ROTATE failed: 0x%x\n", r);
        return 3;
    }

    /* Same capacity check as above */
    const size_t hdr_len = 4 + 4 + 12 + 16;
    if (blob_len < hdr_len)
    {
        fprintf(stderr, "regress-rotate: invalid blob length (%zu < %zu)\n", blob_len, hdr_len);
        return 3;
    }
    const size_t ct_len = blob_len - hdr_len;
    if (ct_len > sizeof(unwrapped))
    {
        fprintf(stderr, "regress-rotate: output buffer too small (%zu < %zu)\n",
                sizeof(unwrapped), ct_len);
        return TEEC_ERROR_SHORT_BUFFER;
    }

    unwrapped_len = sizeof(unwrapped);
    r = do_unwrap(blob, blob_len, unwrapped, &unwrapped_len);
    if (!r)
    {
        fprintf(stderr, "UNWRAP unexpectedly succeeded after rotate (rollback not enforced)\n");
        return 4;
    }
    printf("regress-rotate: OK (unwrap after rotate failed as expected, r=0x%x)\n", r);
    return 0;
}

int main(int argc, char **argv)
{
    int do_test = 0, do_wrap_cmd = 0, do_unwrap_cmd = 0, do_rotate_cmd = 0;
    int do_regress = 0, do_regress_rotate = 0;
    const char *in_path = NULL, *out_path = NULL;

    static const struct option opts[] = {
        {"test", no_argument, 0, 't'},
        {"wrap", no_argument, 0, 'w'},
        {"unwrap", no_argument, 0, 'u'},
        {"rotate", no_argument, 0, 'r'},
        {"regress", no_argument, 0, 1},
        {"regress-rotate", no_argument, 0, 2},
        {"in", required_argument, 0, 'i'},
        {"out", required_argument, 0, 'o'},
        {0, 0, 0, 0}};

    for (;;)
    {
        int idx = 0;
        int c = getopt_long(argc, argv, "twuri:o:", opts, &idx);
        if (c == -1)
            break;
        switch (c)
        {
        case 't':
            do_test = 1;
            break;
        case 'w':
            do_wrap_cmd = 1;
            break;
        case 'u':
            do_unwrap_cmd = 1;
            break;
        case 'r':
            do_rotate_cmd = 1;
            break;
        case 'i':
            in_path = optarg;
            break;
        case 'o':
            out_path = optarg;
            break;
        case 1:
            do_regress = 1;
            break;
        case 2:
            do_regress_rotate = 1;
            break;
        default:
            usage(argv[0]);
            return 1;
        }
    }

    if (do_test + do_wrap_cmd + do_unwrap_cmd + do_rotate_cmd + do_regress + do_regress_rotate != 1)
    {
        usage(argv[0]);
        return 1;
    }

    /* Self-test */
    if (do_test)
    {
        char buf[128];
        size_t len = sizeof(buf);
        TEEC_Result r = run_selftest(buf, &len);
        if (r)
            return 2;
        printf("%s\n", buf);
        return 0;
    }

    /* Rotate */
    if (do_rotate_cmd)
    {
        TEEC_Result r = do_rotate();
        if (!r)
            printf("KEK rotated successfully\n");
        return r ? 3 : 0;
    }

    /* Regress modes */
    if (do_regress)
        return cmd_regress();
    if (do_regress_rotate)
        return cmd_regress_rotate();

    /* File-based wrap/unwrap */
    if (!in_path || !out_path)
    {
        usage(argv[0]);
        return 1;
    }

    uint8_t *in_buf = NULL;
    size_t in_len = 0;
    if (read_file(in_path, &in_buf, &in_len) != 0)
        return 4;

    int rc = 0;
    if (do_wrap_cmd)
    {
        /* allocate output: header (36) + pt_len; give some headroom */
        size_t out_cap = in_len + 64;
        uint8_t *out_buf = malloc(out_cap);
        if (!out_buf)
        {
            free(in_buf);
            return 5;
        }

        size_t blob_len = out_cap;
        TEEC_Result r = do_wrap(in_buf, in_len, out_buf, &blob_len);
        if (r)
        {
            fprintf(stderr, "WRAP failed: 0x%x\n", r);
            rc = 6;
        }
        else if (write_file(out_path, out_buf, blob_len) != 0)
        {
            rc = 7;
        }
        else
        {
            printf("Wrapped %zu bytes -> %zu bytes\n", in_len, blob_len);
        }

        free(out_buf);
        free(in_buf);
        return rc;
    }

    if (do_unwrap_cmd)
    {
        /* plaintext capacity: ciphertext length = blob_len - header_size */
        const size_t hdr_len = 4 + 4 + 12 + 16; /* 36 */
        size_t pt_cap = (in_len > hdr_len) ? (in_len - hdr_len) : 0;
        uint8_t *pt_buf = malloc(pt_cap ? pt_cap : 1); /* avoid malloc(0) */
        if (!pt_buf)
        {
            free(in_buf);
            return 5;
        }

        size_t pt_len = pt_cap;
        TEEC_Result r = do_unwrap(in_buf, in_len, pt_buf, &pt_len);
        if (r)
        {
            fprintf(stderr, "UNWRAP failed: 0x%x\n", r);
            rc = 6;
        }
        else if (write_file(out_path, pt_buf, pt_len) != 0)
        {
            rc = 7;
        }
        else
        {
            printf("Unwrapped %zu bytes -> %zu bytes\n", in_len, pt_len);
        }

        free(pt_buf);
        free(in_buf);
        return rc;
    }

    free(in_buf);
    return 0;
}
/* End of optee_get_key.c */
