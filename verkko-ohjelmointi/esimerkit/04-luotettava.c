// Luotettava siirto UDP:n päällä: pysähdy ja odota -protokolla
// (stop-and-wait ARQ). Kanava pudottaa ja monistaa paketteja
// toistettavasti; järjestysnumerot, kuittaukset ja uudelleenlähetys
// korjaavat sen.
#define _GNU_SOURCE
#include <poll.h>

#include "verkko.h"

enum { DATA = 1, KUITTAUS = 2, LOPPU = 3, VIESTEJA = 20 };
enum { AIKARAJA_MS = 150 };

// @alku paketti
// Paketti: tyyppi (1 tavu), 3 tavua täytettä, järjestysnumero (4 tavua,
// verkon tavujärjestys) ja enintään 32 tavua dataa.
typedef struct {
    uint8_t tyyppi;
    uint32_t nro;
    char data[33];
} paketti;

static size_t pakkaa(const paketti *p, unsigned char *b) {
    size_t n = strlen(p->data);
    uint32_t nro = htonl(p->nro);
    b[0] = p->tyyppi;
    b[1] = b[2] = b[3] = 0;
    memcpy(b + 4, &nro, 4);
    memcpy(b + 8, p->data, n);
    return 8 + n;
}

static bool pura(const unsigned char *b, size_t n, paketti *p) {
    if (n < 8 || n > 8 + 32) {
        return false;                    // rikkinäinen paketti
    }
    uint32_t nro;
    memcpy(&nro, b + 4, 4);
    *p = (paketti){.tyyppi = b[0], .nro = ntohl(nro)};
    memcpy(p->data, b + 8, n - 8);
    return true;
}
// @loppu paketti

// @alku kanava
// Häviöllinen kanava: 25 % paketeista katoaa ja 10 % monistuu.
typedef struct {
    int fd;
    satunnainen s;
    int pudotettu;
} kanava;

static void laheta(kanava *k, const paketti *p) {
    unsigned char b[64];
    size_t n = pakkaa(p, b);
    uint32_t arpa = satunnainen_alle(&k->s, 100);
    if (arpa < 25) {
        k->pudotettu++;
        return;
    }
    TARKISTA(send(k->fd, b, n, 0));
    if (arpa < 35) {
        TARKISTA(send(k->fd, b, n, 0));
    }
}

// Odottaa pakettia enintään ms millisekuntia. false = aikakatkaisu.
static bool vastaanota(kanava *k, paketti *p, int ms) {
    struct pollfd odotus = {.fd = k->fd, .events = POLLIN};
    while (TARKISTA(poll(&odotus, 1, ms)) == 1) {
        unsigned char b[64];
        ssize_t n = TARKISTA(recv(k->fd, b, sizeof b, 0));
        if (pura(b, (size_t)n, p)) {
            return true;
        }
    }
    return false;
}
// @loppu kanava

// @alku vastaanottaja
static int vastaanottaja(void *arg) {
    kanava k = {.fd = *(int *)arg, .s = {7}};
    uint32_t odotettu = 0;
    int kaksoiskappaleita = 0;
    bool ok = true, lopussa = false;
    paketti p;
    // Loppukuittauksen jälkeen odotetaan sekunti: jos kuittaus katosi,
    // lähettäjä toistaa LOPPU-paketin, ja se kuitataan uudelleen.
    while (vastaanota(&k, &p, lopussa ? 1000 : 5000)) {
        if (p.tyyppi == DATA && p.nro == odotettu) {
            char oikea[33];
            snprintf(oikea, sizeof oikea, "viesti %u", (unsigned)p.nro);
            ok = ok && strcmp(p.data, oikea) == 0;
            odotettu++;                  // toimitetaan sovellukselle
        } else if (p.tyyppi == DATA) {
            kaksoiskappaleita++;         // jo saatu: kuitataan uudelleen
        }
        lopussa = lopussa || (p.tyyppi == LOPPU && p.nro == odotettu);
        if (p.nro < odotettu || lopussa) {
            laheta(&k, &(paketti){.tyyppi = KUITTAUS, .nro = p.nro});
        }
    }
    printf("vastaanottaja: %u viestiä oikeassa järjestyksessä: %s\n",
           (unsigned)odotettu, ok ? "kyllä" : "ei");
    printf("vastaanottaja: kaksoiskappaleita hylättiin: %s\n",
           kaksoiskappaleita > 0 ? "kyllä" : "ei");
    return ok && lopussa && odotettu == VIESTEJA ? 0 : 1;
}
// @loppu vastaanottaja

// @alku lahettaja
// Lähettää paketin, kunnes sen kuittaus saapuu. Palauttaa yritykset.
static int laheta_luotettavasti(kanava *k, const paketti *p) {
    for (int yritys = 1; yritys <= 30; yritys++) {
        laheta(k, p);
        paketti vastaus;
        while (vastaanota(k, &vastaus, AIKARAJA_MS)) {
            if (vastaus.tyyppi == KUITTAUS && vastaus.nro == p->nro) {
                return yritys;
            }                            // vanha kuittaus: ohitetaan
        }
    }
    return -1;                           // vastapuoli ei vastaa
}
// @loppu lahettaja

int main(void) {
    vahtikoira();
    int pari[2];                         // yhdistetyt UDP-soketit
    struct sockaddr_in osoitteet[2];
    for (int i = 0; i < 2; i++) {
        pari[i] = (int)TARKISTA(socket(AF_INET, SOCK_DGRAM, 0));
        osoitteet[i] = (struct sockaddr_in){
            .sin_family = AF_INET, .sin_addr.s_addr = htonl(INADDR_LOOPBACK)};
        TARKISTA(bind(pari[i], (struct sockaddr *)&osoitteet[i],
                      sizeof osoitteet[i]));
        socklen_t pituus = sizeof osoitteet[i];
        TARKISTA(getsockname(pari[i], (struct sockaddr *)&osoitteet[i],
                             &pituus));
    }
    for (int i = 0; i < 2; i++) {
        TARKISTA(connect(pari[i], (struct sockaddr *)&osoitteet[1 - i],
                         sizeof osoitteet[1 - i]));
    }
    pid_t pid = kaynnista(vastaanottaja, &pari[1]);

    kanava k = {.fd = pari[0], .s = {42}};
    int uudelleen = 0;
    for (uint32_t i = 0; i <= VIESTEJA; i++) {
        paketti p = {.tyyppi = i < VIESTEJA ? DATA : LOPPU, .nro = i};
        snprintf(p.data, sizeof p.data, "viesti %u", (unsigned)i);
        int yrityksia = laheta_luotettavasti(&k, &p);
        if (yrityksia == -1) {
            return 1;
        }
        uudelleen += yrityksia - 1;
    }
    int tulos = odota(pid);              // vastaanottaja tulostaa ensin
    printf("lähettäjä: kaikki kuitattu, kanava pudotti paketteja: %s, "
           "uudelleenlähetyksiä: %s\n", k.pudotettu > 0 ? "kyllä" : "ei",
           uudelleen > 0 ? "kyllä" : "ei");
    close(pari[0]);
    close(pari[1]);
    return tulos;
}
