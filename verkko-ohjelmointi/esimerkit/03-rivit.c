// Viestien rajaus erottimella: tekstiprotokolla, jossa jokainen komento
// on oma rivinsä (CRLF tai LF). Lukija puskuroi, koska yksi recv voi
// tuoda puolikkaan rivin tai monta riviä.
#define _GNU_SOURCE
#include <netinet/tcp.h>
#include <time.h>

#include "verkko.h"

static uint16_t portti;

// @alku lukija
typedef struct {
    int fd;
    char puskuri[128];                   // myös rivin enimmäispituus
    size_t alku, loppu;                  // lukematon data [alku, loppu)
} rivilukija;

// Kopioi seuraavan rivin ilman rivinvaihtoa. Palauttaa 1, 0 (yhteys
// sulkeutui rivien välissä) tai -1 (virhe, liian pitkä tai kesken jäänyt
// rivi).
static int lue_rivi(rivilukija *r, char *rivi, size_t koko) {
    for (;;) {
        char *lf = (char *)memchr(r->puskuri + r->alku, '\n',
                                  r->loppu - r->alku);
        if (lf != nullptr) {
            size_t n = (size_t)(lf - (r->puskuri + r->alku));
            if (n > 0 && lf[-1] == '\r') {
                n--;                     // CRLF
            }
            if (n >= koko) {
                errno = EMSGSIZE;
                return -1;
            }
            memcpy(rivi, r->puskuri + r->alku, n);
            rivi[n] = '\0';
            r->alku = (size_t)(lf - r->puskuri) + 1;
            return 1;
        }
        if (r->alku > 0) {               // siirrä vajaa rivi alkuun
            memmove(r->puskuri, r->puskuri + r->alku, r->loppu - r->alku);
            r->loppu -= r->alku;
            r->alku = 0;
        }
        if (r->loppu == sizeof r->puskuri) {
            errno = EMSGSIZE;            // rivi ei mahdu puskuriin
            return -1;
        }
        ssize_t k = recv(r->fd, r->puskuri + r->loppu,
                         sizeof r->puskuri - r->loppu, 0);
        if (k == 0) {
            errno = EPROTO;
            return r->loppu == 0 ? 0 : -1;
        }
        if (k == -1 && errno != EINTR) {
            return -1;
        }
        r->loppu += k > 0 ? (size_t)k : 0;
    }
}
// @loppu lukija

// @alku asiakas
// Lähettää komennot tarkoituksella hankalina paloina.
static int asiakas(void *) {
    int fd = yhdista(portti);
    int paalla = 1;                      // ei Naglen algoritmia: palat
    TARKISTA(setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &paalla,
                        sizeof paalla)); // lähtevät erikseen
    const char *palat[] = {"LISAA omena 3\r\nLIS", "AA pa",
                           "ppa", "ri 2\r\nTULOSTA\r\nLOPETA\r\n"};
    for (size_t i = 0; i < 4; i++) {
        TARKISTA(kirjoita_kaikki(fd, palat[i], strlen(palat[i])));
        nanosleep(&(struct timespec){.tv_nsec = 10'000'000}, nullptr);
    }
    close(fd);
    return 0;
}
// @loppu asiakas

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(asiakas, nullptr);
    rivilukija r = {.fd = (int)TARKISTA(accept(kuuntelija, nullptr,
                                               nullptr))};
    char rivi[64];
    int tulos;
    while ((tulos = lue_rivi(&r, rivi, sizeof rivi)) == 1) {
        printf("komento: \"%s\"\n", rivi);
    }
    puts(tulos == 0 ? "yhteys sulkeutui" : strerrorname_np(errno));
    close(r.fd);
    odota(pid);
    close(kuuntelija);
    return 0;
}
