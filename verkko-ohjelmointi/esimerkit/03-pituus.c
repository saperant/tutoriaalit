// Viestien rajaus pituusetuliitteellä: 4 tavun pituus verkon
// tavujärjestyksessä ja sen jälkeen viestin tavut. Vastaanottaja
// tarkistaa pituuden ennen kuin varaa muistia.
#define _GNU_SOURCE
#include <sys/uio.h>

#include "verkko.h"

enum { MAKSIMI = 1 << 20 };              // suurin sallittu viesti
static uint16_t portti;

// @alku laheta
// Otsake ja data yhdellä kutsulla (writev), jotta ne eivät lähde kahtena
// pienenä segmenttinä. Lyhyt kirjoitus jatketaan kirjoita_kaikki-kutsulla.
static int laheta_viesti(int fd, const void *data, uint32_t n) {
    uint32_t otsake = htonl(n);
    struct iovec osat[2] = {{&otsake, 4}, {(void *)data, n}};
    ssize_t k = writev(fd, osat, 2);
    if (k == -1) {
        return -1;
    }
    if (k < 4) {                         // harvinaista, mutta mahdollista
        if (kirjoita_kaikki(fd, (char *)&otsake + k, 4 - (size_t)k) == -1) {
            return -1;
        }
        k = 4;
    }
    return kirjoita_kaikki(fd, (const char *)data + (k - 4),
                           n - (size_t)(k - 4));
}
// @loppu laheta

// @alku vastaanota
// Palauttaa 1 ja viestin (*data, *pituus), 0 kun yhteys sulkeutui
// viestien välissä, ja -1 virheessä. Liian suuri pituus on
// protokollavirhe: muuten vastapuoli voisi pakottaa varaamaan 4 GiB.
static int vastaanota_viesti(int fd, char **data, uint32_t *pituus) {
    uint32_t otsake;
    int tulos = lue_tasan(fd, &otsake, 4);
    if (tulos <= 0) {
        return tulos;
    }
    uint32_t n = ntohl(otsake);
    if (n > MAKSIMI) {
        errno = EMSGSIZE;
        return -1;
    }
    char *p = (char *)malloc(n + 1);     // +1: myös n = 0 kelpaa
    tulos = n > 0 ? lue_tasan(fd, p, n) : 1;
    if (tulos != 1) {
        free(p);
        errno = tulos == 0 ? EPROTO : errno;  // loppui kesken viestin
        return -1;
    }
    *data = p;
    *pituus = n;
    return 1;
}
// @loppu vastaanota

static int asiakas(void *) {
    int fd = yhdista(portti);
    char *iso = (char *)calloc(100000, 1);
    TARKISTA(laheta_viesti(fd, "", 0));
    TARKISTA(laheta_viesti(fd, "hei", 3));
    TARKISTA(laheta_viesti(fd, iso, 100000));
    uint32_t valhe = htonl(0x7fffffff);  // väittää viestiä 2 GiB:ksi
    TARKISTA(kirjoita_kaikki(fd, &valhe, 4));
    free(iso);
    char c;
    recv(fd, &c, 1, 0);                  // odota, että palvelin sulkee
    close(fd);
    return 0;
}

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(asiakas, nullptr);
    int yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    // @alku silmukka
    for (;;) {
        char *data;
        uint32_t n;
        int tulos = vastaanota_viesti(yhteys, &data, &n);
        if (tulos == 0) {
            puts("yhteys sulkeutui");
            break;
        }
        if (tulos == -1) {
            printf("hylätään yhteys: %s\n", strerrorname_np(errno));
            break;
        }
        printf("viesti: %u tavua\n", n);
        free(data);
    }
    // @loppu silmukka
    close(yhteys);
    odota(pid);
    close(kuuntelija);
    return 0;
}
