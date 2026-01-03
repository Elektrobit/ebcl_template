#ifndef __MY_TA_DATA_KEY_H__
#define __MY_TA_DATA_KEY_H__

/* ===== UUID + command IDs must match the TA ===== */

/* UUID {65024bcf-47a0-4a08-9498-bb634c46ec9e} */
#define KEKSTORE_TA_UUID { \
    0x65024bcf, 0x47a0, 0x4a08, {0x94, 0x98, 0xbb, 0x63, 0x4c, 0x46, 0xec, 0x9e}}
enum
{
    CMD_WRAP = 0x0001,   /* INOUT: plaintext -> IV|TAG|CIPHERTEXT */
    CMD_UNWRAP = 0x0002, /* INOUT: IV|TAG|CIPHERTEXT -> plaintext */
    CMD_TEST = 0x0003,   /* INOUT: returns status text */
    CMD_ROTATE_KEK = 0x0004
};
#endif