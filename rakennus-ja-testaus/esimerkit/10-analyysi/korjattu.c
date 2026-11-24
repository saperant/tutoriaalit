// Sama toiminnallisuus korjattuna: kaikki kolme työkalua hiljaa.
#include <errno.h>
#include <stdlib.h>
#include <string.h>

// Jäsentää rivin "nimi=arvo". Palauttaa 0 tai -1, jos rivi ei kelpaa.
int lue_asetus(const char *rivi, char *nimi, size_t koko, long *arvo)
{
    const char *erotin = strchr(rivi, '=');
    if (erotin == NULL)
        return -1;
    size_t pituus = (size_t)(erotin - rivi);
    if (pituus >= koko)
        return -1;
    memcpy(nimi, rivi, pituus);
    nimi[pituus] = '\0';

    char *loppu;
    errno = 0;
    *arvo = strtol(erotin + 1, &loppu, 10);
    if (errno != 0 || loppu == erotin + 1 || *loppu != '\0')
        return -1;
    return 0;
}

// Palauttaa kopion tunnisteesta tai NULL (liian pitkä tai muisti loppu).
char *kopioi_tunniste(const char *tunniste)
{
    size_t pituus = strlen(tunniste);
    if (pituus >= 16)
        return NULL;
    char *kopio = malloc(pituus + 1);
    if (kopio == NULL)
        return NULL;
    memcpy(kopio, tunniste, pituus + 1);
    return kopio;
}

// Viimeinen kolmesta oletusarvosta.
int viimeinen_oletus(void)
{
    static const int oletukset[3] = {10, 20, 30};
    return oletukset[2];
}
