// Siisti sammutus: SIGTERM tulee tapahtumasilmukkaan signalfd-kuvaajana.
// Palvelin lopettaa uusien yhteyksien hyväksymisen, vie kesken olevan
// työn loppuun, ilmoittaa lopettavansa (shutdown SHUT_WR) ja odottaa,
// että asiakas sulkee yhteyden.
#define _GNU_SOURCE
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/timerfd.h>

#include "verkko.h"

static uint16_t portti;
static int kuuntelija;

// @alku palvelin
static int palvelin(void *) {
    sigset_t term;
    sigemptyset(&term);
    sigaddset(&term, SIGTERM);
    TARKISTA(sigprocmask(SIG_BLOCK, &term, nullptr));  // vain signalfd:lle
    int sfd = (int)TARKISTA(signalfd(-1, &term, SFD_CLOEXEC));
    int tyo = (int)TARKISTA(timerfd_create(CLOCK_MONOTONIC, 0));
    int ep = (int)TARKISTA(epoll_create1(EPOLL_CLOEXEC));
    int kuvaajat[] = {kuuntelija, sfd, tyo};
    for (int i = 0; i < 3; i++) {
        struct epoll_event e = {.events = EPOLLIN, .data.fd = kuvaajat[i]};
        TARKISTA(epoll_ctl(ep, EPOLL_CTL_ADD, kuvaajat[i], &e));
    }
    int asiakas = -1;
    bool sammutetaan = false, kesken = false;
    while (!sammutetaan || kesken) {
        struct epoll_event e;
        TARKISTA(epoll_wait(ep, &e, 1, -1));
        if (e.data.fd == kuuntelija) {
            asiakas = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
            char pyynto[16];             // "HIDAS": 300 ms:n työ
            TARKISTA(recv(asiakas, pyynto, sizeof pyynto, 0));
            dprintf(asiakas, "ALOITETTU\n");
            struct itimerspec t = {.it_value.tv_nsec = 300'000'000};
            TARKISTA(timerfd_settime(tyo, 0, &t, nullptr));
            kesken = true;
        } else if (e.data.fd == tyo) {
            uint64_t n;
            TARKISTA(read(tyo, &n, sizeof n));
            dprintf(asiakas, "VALMIS\n");
            kesken = false;
        } else {                         // SIGTERM
            struct signalfd_siginfo tieto;
            TARKISTA(read(sfd, &tieto, sizeof tieto));
            close(kuuntelija);           // uudet yhteydet: ECONNREFUSED
            sammutetaan = true;
        }
    }
    TARKISTA(shutdown(asiakas, SHUT_WR));   // "en lähetä enempää"
    char c;
    while (recv(asiakas, &c, 1, 0) > 0) {   // odota asiakkaan sulkemista
    }
    close(asiakas);
    close(tyo);
    close(sfd);
    close(ep);
    return 0;
}
// @loppu palvelin

int main(void) {
    vahtikoira();
    kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(palvelin, nullptr);
    close(kuuntelija);
    // @alku kulku
    int fd = yhdista(portti);
    FILE *sisaan = fdopen(fd, "r");
    TARKISTA(kirjoita_kaikki(fd, "HIDAS\n", 6));
    char rivi[32];
    if (fgets(rivi, sizeof rivi, sisaan) != nullptr) {
        printf("asiakas: %s", rivi);     // työ on käynnissä
    }
    TARKISTA(kill(pid, SIGTERM));
    puts("asiakas: SIGTERM lähetetty kesken työn");
    while (fgets(rivi, sizeof rivi, sisaan) != nullptr) {
        printf("asiakas: %s", rivi);
    }
    puts("asiakas: palvelin sulki yhteyden (EOF)");
    fclose(sisaan);                      // palvelin pääsee lopettamaan

    struct sockaddr_in osoite = {.sin_family = AF_INET,
                                 .sin_port = htons(portti),
                                 .sin_addr.s_addr = htonl(INADDR_LOOPBACK)};
    int uusi = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    int tulos = connect(uusi, (struct sockaddr *)&osoite, sizeof osoite);
    printf("uusi yhteys: %s\n",
           tulos == 0 ? "onnistui" : strerrorname_np(errno));
    close(uusi);
    printf("palvelimen paluuarvo: %d\n", odota(pid));
    // @loppu kulku
    return 0;
}
