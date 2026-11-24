// TCP-kaikupalvelin ja sen asiakas. Palvelin kuuntelee
// silmukkaosoitteessa ytimen valitsemassa portissa, ja asiakas
// (lapsiprosessi) lähettää rivit ja lukee ne takaisin.
#define _GNU_SOURCE
#include "verkko.h"

static uint16_t portti;                  // palvelimen valitsema portti

// @alku asiakas
static int asiakas(void *) {
    int fd = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    struct sockaddr_in palvelin = {};
    palvelin.sin_family = AF_INET;
    palvelin.sin_port = htons(portti);   // isännän tavujärjestyksestä
    TARKISTA(inet_pton(AF_INET, "127.0.0.1", &palvelin.sin_addr));
    TARKISTA(connect(fd, (struct sockaddr *)&palvelin, sizeof palvelin));

    const char *rivit[] = {"hei palvelin\n", "toinen rivi\n", "loppu\n"};
    for (size_t i = 0; i < 3; i++) {
        size_t n = strlen(rivit[i]);
        char vastaus[64] = {};
        TARKISTA(kirjoita_kaikki(fd, rivit[i], n));
        if (lue_tasan(fd, vastaus, n) != 1) {
            return 1;
        }
        printf("asiakas sai takaisin: %s", vastaus);
    }
    TARKISTA(close(fd));
    return 0;
}
// @loppu asiakas

int main(void) {
    vahtikoira();
    // @alku palvelin
    int kuuntelija = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    struct sockaddr_in osoite = {};
    osoite.sin_family = AF_INET;
    osoite.sin_port = htons(0);          // 0 = ydin valitsee vapaan
    osoite.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    TARKISTA(bind(kuuntelija, (struct sockaddr *)&osoite, sizeof osoite));
    TARKISTA(listen(kuuntelija, SOMAXCONN));
    socklen_t pituus = sizeof osoite;
    TARKISTA(getsockname(kuuntelija, (struct sockaddr *)&osoite,
                         &pituus));
    portti = ntohs(osoite.sin_port);
    // @loppu palvelin

    pid_t pid = kaynnista(asiakas, nullptr);

    // @alku palvele
    struct sockaddr_in vertainen;
    pituus = sizeof vertainen;
    int yhteys = (int)TARKISTA(accept(kuuntelija,
                                      (struct sockaddr *)&vertainen,
                                      &pituus));
    char nimi[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &vertainen.sin_addr, nimi, sizeof nimi);
    long tavuja = 0;
    char puskuri[4096];
    ssize_t n;
    while ((n = TARKISTA(recv(yhteys, puskuri, sizeof puskuri, 0))) > 0) {
        TARKISTA(kirjoita_kaikki(yhteys, puskuri, (size_t)n));
        tavuja += n;
    }                                    // 0 = asiakas sulki yhteyden
    TARKISTA(close(yhteys));
    // @loppu palvele
    TARKISTA(close(kuuntelija));
    if (odota(pid) != 0) {
        return 1;
    }
    printf("palvelin: asiakas %s, kaiutettu %ld tavua\n", nimi, tavuja);
    return 0;
}
