#include <stdio.h>
#include <unistd.h>

int main(void) {
    int i;

    for (i = 0; i < 100; i++) {
        printf("Hello, World! (Iteration %d)\n", i + 1);
        
        printf("Sleeping for 10 seconds...\n");
        sleep(10);
    }

    return 0;
}
