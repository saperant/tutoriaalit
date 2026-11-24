/* Tulostaa pinon, keon, ohjelman ja C-kirjaston osoitteet, jotta
 * ASLR:n vaikutus näkyy ajosta toiseen. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int paikallinen = 0;
    void *keko = malloc(16);
    printf("pino %#jx\n", (uintmax_t)(uintptr_t)&paikallinen);
    printf("keko %#jx\n", (uintmax_t)(uintptr_t)keko);
    printf("ohjelma %#jx\n", (uintmax_t)(uintptr_t)&main);
    printf("libc %#jx\n", (uintmax_t)(uintptr_t)stdout);  /* FILE-olio */
    free(keko);
    return 0;
}
