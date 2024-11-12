/**
* Copyright (c) 2024 Elektrobit Automotive GmbH
* License: MIT
**/

#ifndef SHMLIB_LOGGER_H
#define SHMLIB_LOGGER_H

enum shmlib_logger_level {
    SHMLIB_LOGGER_DEBUG,
    SHMLIB_LOGGER_INFO,
    SHMLIB_LOGGER_ERROR,
    SHMLIB_LOGGER_MAX,
};

/**
 * @brief Logs a message with the specified log level.
 *
 * This macro logs a message with the pid and specified log level, formatted using the specified format string and
 * arguments.
 *
 * The default log level is SHMLIB_LOGGER_INFO. Anything with a level lower than this (i.e. SHMLIB_LOGGER_DEBUG)
 * will not be printed out unless shmlib_logger_set_min_log_level() is called with the appropriate value.
 *
 * @param log_level The log level of the message.
 * @param format The format string for the message.
 * @param ... The arguments to the format string.
 *
 * @return 0 on success, -ENOSPC if the log message is too big, or -EIO if the logger has not yet been initialised.
 */
int shmlib_log(enum shmlib_logger_level level, const char* fmt, ...);

/**
 * @brief Set the minimum log level that should be printed.
 *
 * @param log_level The minimum log level.
 *
 * @return 0 on success, -EINVAL if the log level is not valid.
 */
int shmlib_logger_set_min_log_level(enum shmlib_logger_level level);

/**
 * @brief Set a tag that should be prepended to all log messages.
 *
 * This can be NULL to disable the tag.
 *
 * @param tag String representing the tag
 */
void shmlib_logger_set_tag(const char* tag);

/**
 * @brief Logs an error saying the given function failed alongside the error code.
 *
 * @param function_name Function name that failed.
 * @param error_code Error code to print.
 *
 * @return 0 on success, -ENOSPC if the log message is too big, or -EIO if the logger has not yet been initialised.
 */
int shmlib_log_function_failed(const char* function_name, int error_code);

/**
 * @brief Logs an error message with the string representation of the given error code appended.
 *
 * @param error_code Error code to print.
 * @param format The format string for the message.
 * @param ... The arguments to the format string.
 *
 * @return 0 on success, -ENOSPC if the log message is too big, or -EIO if the logger has not yet been initialised.
 */
int shmlib_log_with_error_code(int error_code, const char* fmt, ...);

#endif /* SHMLIB_LOGGER_H */
