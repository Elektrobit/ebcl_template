#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>

int main() {
    // Open the syslog
    openlog("meminfo_reader", LOG_PID | LOG_CONS, LOG_USER);

    // Open the /proc/meminfo file
    FILE *fp = fopen("/proc/meminfo", "r");
    if (fp == NULL) {
        syslog(LOG_ERR, "Failed to open /proc/meminfo");
        closelog();
        return 1;
    }

    char line[256];
    long available_mem = 0;

    // Read the file line by line
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (sscanf(line, "MemAvailable: %ld kB", &available_mem) == 1) {
            syslog(LOG_ALERT, "Available memory: %ld kB", available_mem);
            break;
        }
    }

    // Close the file
    fclose(fp);

    // Close the syslog
    closelog();

    return 0;
}
