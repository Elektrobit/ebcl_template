/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>

#include "shmlib_logger.h"

static enum shmlib_logger_level min_log_level = SHMLIB_LOGGER_INFO;
static const char* logger_tag = NULL;

enum {
    MAX_LOG_PREFIX_SIZE = 128,
    MAX_LOG_SIZE = (4096 - MAX_LOG_PREFIX_SIZE - 1),
    STRERROR_BUF_SIZE = 256, /**< Probably big enough for all possible localised error messages */
};

static const char* shmlib_logger_get_level_label(const enum shmlib_logger_level level)
{
    switch (level) {
    case SHMLIB_LOGGER_ERROR:
        return "ERROR";
    case SHMLIB_LOGGER_INFO:
        return "INFO";
    case SHMLIB_LOGGER_DEBUG:
        return "DEBUG";
    default:
        return "UNKNOWN";
    }
}

int shmlib_log(const enum shmlib_logger_level level, const char* const fmt, ...)
{
    char buffer[MAX_LOG_SIZE] = {'\0'};
    va_list args = {0};

    /* Do nothing if the log level is too low */
    if (level < min_log_level) {
        return 0;
    }

    va_start(args, fmt);
    (void)vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);

    if (logger_tag) {
        printf("%s: ", logger_tag);
    }
    printf("%s: %s\n", shmlib_logger_get_level_label(level), buffer);

    return 0;
}

int shmlib_logger_set_min_log_level(const enum shmlib_logger_level level)
{
    if (level < SHMLIB_LOGGER_DEBUG || level >= SHMLIB_LOGGER_MAX) {
        return -EINVAL;
    }

    min_log_level = level;

    return 0;
}

int shmlib_log_function_failed(const char* const function_name, int error_code)
{
    return shmlib_log_with_error_code(error_code, "%s() failed", function_name);
}

int shmlib_log_with_error_code(int error_code, const char* const fmt, ...)
{
    char err_buf[STRERROR_BUF_SIZE] = {'\0'};
    char buffer[MAX_LOG_SIZE] = {'\0'};
    va_list args = {0};

    va_start(args, fmt);
    (void)vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);

    if (error_code < 0) {
        error_code = -error_code;
    }

    strerror_r(error_code, err_buf, sizeof(err_buf));

    return shmlib_log(SHMLIB_LOGGER_ERROR, "%s: %s (%d)", buffer, err_buf, -error_code);
}

void shmlib_logger_set_tag(const char* const tag)
{
    logger_tag = tag;
}
