// Asetustiedoston käsittelyä, jossa on tavallisia virheitä. Kääntäjä,
// clang-tidy ja cppcheck löytävät kukin osan niistä.
#include <stdlib.h>
#include <string.h>

// Jäsentää rivin "nimi=arvo": nimi puskuriin, arvo paluuarvona.
int lue_asetus(const char *rivi, char *nimi, size_t koko)
{
    const char *erotin = strchr(rivi, '=');
    if (erotin == NULL)
        return -1;
    int pituus = erotin - rivi;
    if (pituus >= koko)
        return -1;
    memcpy(nimi, rivi, pituus);
    nimi[pituus] = '\0';
    return atoi(erotin + 1);
}

// Palauttaa kopion tunnisteesta tai NULL, jos tunniste on liian pitkä.
char *kopioi_tunniste(const char *tunniste)
{
    char *kopio = malloc(16);
    if (strlen(tunniste) >= 16)
        return NULL;
    strcpy(kopio, tunniste);
    return kopio;
}

// Viimeinen kolmesta oletusarvosta.
int viimeinen_oletus(void)
{
    int oletukset[3] = {10, 20, 30};
    return oletukset[3];
}
