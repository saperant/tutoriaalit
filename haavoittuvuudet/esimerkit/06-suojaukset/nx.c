/* NX: yritetään suorittaa pinossa olevaa dataa. Data on yksi ret-käsky
 * (0xc3), joka vain palaa: jos pino ei ole suoritettavaa, prosessori
 * kieltäytyy ja ohjelma saa SIGSEGV:n. */
#include <stdio.h>
#include <string.h>

// @alku nx
int main(void)
{
    unsigned char koodi[16];
    memset(koodi, 0xc3, sizeof koodi);  /* x86-64: ret */
    void (*funktio)(void) = (void (*)(void))(void *)koodi;
    funktio();
    puts("pinossa olevaa dataa suoritettiin");
    return 0;
}
// @loppu nx
