/* Allekirjoitusten lähde: ohjelma, joka käyttää samoja C-kirjaston
 * funktioita kuin tutkittava laite ja joka käännetään samalla
 * työkaluketjulla (arm-none-eabi-gcc, newlib-nano). Sen symbolitaulu
 * kertoo, mitkä tavut kuuluvat millekin kirjastofunktiolle. */
#include <string.h>

volatile char puskuri[64];
volatile size_t koko = 16;

int main(void) {
    char *p = (char *)puskuri;
    memset(p, 'a', koko);
    memcpy(p + 32, p, koko);
    int tulos = strcmp(p, p + 1) + strncmp(p, p + 2, koko);
    tulos += (int)strlen(p) + (strchr(p, 'b') != NULL);
    tulos += memcmp(p, p + 4, koko);
    return tulos;
}
