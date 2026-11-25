// Sumutuskohde: libFuzzer kutsuu funktiota LLVMFuzzerTestOneInput
// yhä uusilla syötteillä ja ohjaa muuntelua kattavuuden perusteella.
#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

// @alku jasennin
// Jäsentää rivin "nimi=luku". Palauttaa false, jos rivi on virheellinen.
static bool jasenna(const char *rivi, size_t n, long *arvo)
{
    size_t i = 0;
    while (i < n && rivi[i] != '=') {
        i++;
    }
    if (i == 0 || i >= n) {
        return false;            // nimi tai yhtäsuuruusmerkki puuttuu
    }
    char numero[8];
    size_t k = 0;
    for (i++; i < n && isdigit((unsigned char)rivi[i]); i++) {
        numero[k++] = rivi[i];   // virhe: k:ta ei rajata
    }
    if (k == 0 || i != n) {
        return false;
    }
    numero[k] = '\0';
    *arvo = strtol(numero, nullptr, 10);
    return true;
}
// @loppu jasennin

// @alku kohde
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t n)
{
    long arvo;
    jasenna((const char *)data, n, &arvo);
    return 0;
}
// @loppu kohde
