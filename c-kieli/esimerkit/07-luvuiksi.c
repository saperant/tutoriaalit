#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

// @alku jasenna
// Muuntaa koko merkkijonon long-luvuksi. Palauttaa false virheessä.
bool jasenna_luku(const char *teksti, long *tulos)
{
    char *loppu;
    errno = 0;
    long arvo = strtol(teksti, &loppu, 10);
    if (loppu == teksti || *loppu != '\0') {
        return false;   // ei numeroita tai ylimääräisiä merkkejä
    }
    if (errno == ERANGE) {
        return false;   // ei mahdu long-tyyppiin
    }
    *tulos = arvo;
    return true;
}
// @loppu jasenna

int main(void)
{
    // @alku kaytto
    const char *syotteet[] = {
        "123", "-45", "12abc", "", "99999999999999999999",
    };
    for (size_t i = 0; i < sizeof syotteet / sizeof syotteet[0]; ++i) {
        long luku;
        if (jasenna_luku(syotteet[i], &luku)) {
            printf("\"%s\" -> %ld\n", syotteet[i], luku);
        } else {
            printf("\"%s\" -> virhe\n", syotteet[i]);
        }
    }
    printf("atoi(\"12abc\") = %d\n", atoi("12abc"));   // ei virheilmoitusta
    // @loppu kaytto
}
