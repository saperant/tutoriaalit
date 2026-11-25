// Ajaa näytefunktion, jotta sen toiminta tulee testatuksi.
#include <stdio.h>
#include <string.h>

long ensimmainen(void);

void tayta(char *puskuri, long n) {
    memset(puskuri, 'k', (size_t)n);
}

int main(void) {
    printf("ensimmainen: %c\n", (char)ensimmainen());
    return 0;
}
