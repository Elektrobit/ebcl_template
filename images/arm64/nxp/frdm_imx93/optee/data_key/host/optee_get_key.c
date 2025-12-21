
/*
 * optee_get_key.c
 * Host client for OP-TEE TA: test / wrap / unwrap LUKS key blobs.
 * License: BSD-2-Clause
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <getopt.h>
#include <errno.h>
#include <tee_client_api.h>
#include "data_key_ta.h"

/* ===== Common TEEC invocation helper ===== */

static TEEC_Result invoke_cmd(uint32_t cmd, uint8_t *buf, size_t *len)
{
    TEEC_Context ctx;
    TEEC_Session sess;
    TEEC_Operation op;
    TEEC_UUID uuid = KEKSTORE_TA_UUID;
    uint32_t origin;
    TEEC_Result res;

    res = TEEC_InitializeContext(NULL, &ctx);
    if (res != TEEC_SUCCESS)
    {
        fprintf(stderr, "TEEC_InitializeContext failed: 0x%x\n", res);
        return res;
    }

    memset(&op, 0, sizeof(op));

    res = TEEC_OpenSession(&ctx, &sess, &uuid, TEEC_LOGIN_PUBLIC, NULL, NULL, &origin);
    if (res != TEEC_SUCCESS)
    {
        fprintf(stderr, "TEEC_OpenSession failed: 0x%x (origin=0x%x)\n", res, origin);
        TEEC_FinalizeContext(&ctx);
        return res;
    }

    op.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_TEMP_INOUT, TEEC_NONE, TEEC_NONE, TEEC_NONE);
    op.params[0].tmpref.buffer = buf;
    op.params[0].tmpref.size = *len;
    res = TEEC_InvokeCommand(&sess, cmd, &op, &origin);
    if (res == TEEC_SUCCESS)
    {
        *len = op.params[0].tmpref.size;
    }
    else
    {
        fprintf(stderr, "TEEC_InvokeCommand(0x%x) failed: 0x%x (origin=0x%x)\n",
                cmd, res, origin);
    }

    TEEC_CloseSession(&sess);
    TEEC_FinalizeContext(&ctx);
    return res;
}

/* ===== File helpers ===== */

static int read_file(const char *path, uint8_t **buf, size_t *len)
{
    FILE *f = fopen(path, "rb");
    if (!f)
    {
        perror("fopen");
        return -1;
    }
    if (fseek(f, 0, SEEK_END) != 0)
    {
        perror("fseek");
        fclose(f);
        return -1;
    }
    long sz = ftell(f);
    if (sz < 0)
    {
        perror("ftell");
        fclose(f);
        return -1;
    }
    rewind(f);

    *buf = (uint8_t *)malloc((size_t)sz);
    if (!*buf)
    {
        perror("malloc");
        fclose(f);
        return -1;
    }

    size_t rd = fread(*buf, 1, (size_t)sz, f);
    fclose(f);
    if (rd != (size_t)sz)
    {
        fprintf(stderr, "Partial read\n");
        free(*buf);
        return -1;
    }

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
    size_t wr = fwrite(buf, 1, len, f);
    fclose(f);
    if (wr != len)
    {
        fprintf(stderr, "Partial write\n");
        return -1;
    }
    return 0;
}

/* ===== CLI ===== */

static void usage(const char *prog)
{
    fprintf(stderr,
            "Usage:\n"
            "  %s --test\n"
            "  %s --wrap   --in <plaintext.bin> --out <wrapped.bin>\n"
            "  %s --unwrap --in <wrapped.bin>   --out <plaintext.bin>\n"
            "\nNotes:\n"
            "  - --wrap produces IV(12)|TAG(16)|CIPHERTEXT in <wrapped.bin>.\n"
            "  - --unwrap expects that same format and returns plaintext.\n",
            prog, prog, prog);
}

int main(int argc, char **argv)
{
    int do_test = 0, do_wrap = 0, do_unwrap = 0;
    const char *in_path = NULL, *out_path = NULL;

    static const struct option opts[] = {
        {"test", no_argument, 0, 't'},
        {"wrap", no_argument, 0, 'w'},
        {"unwrap", no_argument, 0, 'u'},
        {"in", required_argument, 0, 'i'},
        {"out", required_argument, 0, 'o'},
        {0, 0, 0, 0}};

    for (;;)
    {
        int c = getopt_long(argc, argv, "twi:o:u", opts, NULL);
        if (c == -1)
            break;
        switch (c)
        {
        case 't':
            do_test = 1;
            break;
        case 'w':
            do_wrap = 1;
            break;
        case 'u':
            do_unwrap = 1;
            break;
        case 'i':
            in_path = optarg;
            break;
        case 'o':
            out_path = optarg;
            break;
        default:
            usage(argv[0]);
            return 1;
        }
    }

    if (do_test + do_wrap + do_unwrap != 1)
    {
        usage(argv[0]);
        return 1;
    }

    if (do_test)
    {
        uint8_t buf[128];
        size_t len = sizeof(buf);
        TEEC_Result r = invoke_cmd(CMD_TEST, buf, &len);
        if (r != TEEC_SUCCESS)
            return 2;
        printf("%.*s\n", (int)len, (char *)buf);
        return 0;
    }

    /* Wrap / Unwrap need files */
    if (!in_path || !out_path)
    {
        usage(argv[0]);
        return 1;
    }

    uint8_t *in_buf = NULL;
    size_t in_len = 0;
    if (read_file(in_path, &in_buf, &in_len) != 0)
        return 3;

    /* For wrap, allocate INOUT buffer with extra space for IV+TAG */
    uint8_t *io_buf = NULL;
    size_t io_len = 0;

    if (do_wrap)
    {
        io_len = in_len + 12 + 16;
        io_buf = (uint8_t *)malloc(io_len);
        if (!io_buf)
        {
            perror("malloc");
            free(in_buf);
            return 4;
        }
        memcpy(io_buf, in_buf, in_len);

        size_t call_len = in_len; /* TA expects plaintext length as initial size */
        TEEC_Result r = invoke_cmd(CMD_WRAP, io_buf, &call_len);
        if (r != TEEC_SUCCESS)
        {
            free(io_buf);
            free(in_buf);
            return 5;
        }

        /* call_len is actual wrapped length (IV+TAG+CT) */
        if (write_file(out_path, io_buf, call_len) != 0)
        {
            free(io_buf);
            free(in_buf);
            return 6;
        }
        printf("Wrapped %zu bytes -> %u bytes (IV+TAG+CT) written to %s\n",
               in_len, (unsigned)call_len, out_path);
        free(io_buf);
        free(in_buf);
        return 0;
    }

    if (do_unwrap)
    {
        io_len = in_len; /* INOUT size starts as total wrapped blob size */
        io_buf = (uint8_t *)malloc(io_len);
        if (!io_buf)
        {
            perror("malloc");
            free(in_buf);
            return 4;
        }
        memcpy(io_buf, in_buf, in_len);

        size_t call_len = in_len; /* TA sees IV|TAG|CT of length in_len */
        TEEC_Result r = invoke_cmd(CMD_UNWRAP, io_buf, &call_len);
        if (r != TEEC_SUCCESS)
        {
            free(io_buf);
            free(in_buf);
            return 5;
        }

        if (write_file(out_path, io_buf, call_len) != 0)
        {
            free(io_buf);
            free(in_buf);
            return 6;
        }
        printf("Unwrapped %u bytes (IV+TAG+CT) -> %u bytes plaintext written to %s\n",
               (unsigned)in_len, (unsigned)call_len, out_path);
        free(io_buf);
        free(in_buf);
        return 0;
    }

    /* Should not reach here */
    free(in_buf);
    return 1;
}
