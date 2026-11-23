#include <stddef.h>
#include <stdio.h>
#include <string.h>

// @alku viipale
// Viipale (slice, string view): osoitin ja pituus. Viittaa olemassa
// olevaan dataan kopioimatta ja ilman päättävää nollamerkkiä.
typedef struct {
    const char *data;
    size_t pituus;
} Viipale;

#define VIIPALE(literaali) ((Viipale){literaali, sizeof literaali - 1})

bool viipale_yhtasuuri(Viipale a, Viipale b)
{
    return a.pituus == b.pituus && memcmp(a.data, b.data, a.pituus) == 0;
}

// Erottaa syötteen alusta osan erottimeen asti ja siirtää syötettä.
// Palauttaa false, kun syöte on lopussa.
bool viipale_seuraava(Viipale *syote, char erotin, Viipale *osa)
{
    if (syote->pituus == 0) {
        return false;
    }
    const char *loppu = memchr(syote->data, erotin, syote->pituus);
    size_t n = loppu ? (size_t)(loppu - syote->data) : syote->pituus;
    *osa = (Viipale){syote->data, n};
    size_t ohita = loppu ? n + 1 : n;
    syote->data += ohita;
    syote->pituus -= ohita;
    return true;
}
// @loppu viipale

int main(void)
{
    // @alku kaytto
    const char otsakkeet[] =
        "Host: esimerkki.fi;Accept: text/html;Connection: close";
    Viipale syote = {otsakkeet, strlen(otsakkeet)};
    Viipale rivi;
    while (viipale_seuraava(&syote, ';', &rivi)) {
        Viipale nimi;
        viipale_seuraava(&rivi, ':', &nimi);
        if (viipale_yhtasuuri(nimi, VIIPALE("Accept"))) {
            printf("Accept-arvo:%.*s\n", (int)rivi.pituus, rivi.data);
        } else {
            printf("ohitetaan %.*s\n", (int)nimi.pituus, nimi.data);
        }
    }
    // @loppu kaytto
}
