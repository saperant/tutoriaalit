// TIME_WAIT: yhteyden ensin sulkenut osapuoli pitää osoiteparin varattuna
// noin minuutin. Uudelleen käynnistyvä palvelin tarvitsee siksi
// SO_REUSEADDR-valitsimen.
#define _GNU_SOURCE
#include "verkko.h"

static uint16_t portti;

static int asiakas(void *) {
    int fd = yhdista(portti);
    char c;
    TARKISTA(recv(fd, &c, 1, 0));        // odota palvelimen FIN
    TARKISTA(close(fd));
    return 0;
}

// @alku sido
// Luo kuuntelijan porttiin (0 = ytimen valitsema). Palauttaa soketin tai
// -1, jos bind epäonnistui.
static int kaynnista_palvelin(uint16_t p, bool uudelleenkaytto) {
    int fd = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    int paalla = 1;
    if (uudelleenkaytto) {
        TARKISTA(setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &paalla,
                            sizeof paalla));
    }
    struct sockaddr_in osoite = {};
    osoite.sin_family = AF_INET;
    osoite.sin_port = htons(p);
    osoite.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(fd, (struct sockaddr *)&osoite, sizeof osoite) == -1) {
        printf("bind %s SO_REUSEADDR: %s\n",
               uudelleenkaytto ? "kanssa" : "ilman", strerrorname_np(errno));
        close(fd);
        return -1;
    }
    TARKISTA(listen(fd, SOMAXCONN));
    socklen_t pituus = sizeof osoite;
    TARKISTA(getsockname(fd, (struct sockaddr *)&osoite, &pituus));
    portti = ntohs(osoite.sin_port);
    printf("bind %s SO_REUSEADDR: onnistui\n",
           uudelleenkaytto ? "kanssa" : "ilman");
    return fd;
}
// @loppu sido

int main(void) {
    vahtikoira();
    // @alku kulku
    int kuuntelija = kaynnista_palvelin(0, true);
    pid_t pid = kaynnista(asiakas, nullptr);
    int yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    TARKISTA(close(yhteys));             // palvelin sulkee ensin
    odota(pid);                          // asiakas on sulkenut omansa
    TARKISTA(close(kuuntelija));         // palvelin pysähtyy

    puts("-- palvelin käynnistyy uudelleen samaan porttiin:");
    int uusi = kaynnista_palvelin(portti, false);  // TIME_WAIT estää
    if (uusi == -1) {
        uusi = kaynnista_palvelin(portti, true);
    }
    // @loppu kulku
    close(uusi);
    return 0;
}
