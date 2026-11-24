// Yksisäikeinen palvelin poll-kutsulla: yksi taulukko kertoo ytimelle
// kaikki seurattavat soketit, ja palvelin käsittelee ne, jotka ovat
// valmiina.
#define _GNU_SOURCE
#include <poll.h>

#include "nelio.h"

enum { ASIAKKAITA = 50, KIERROKSIA = 10, MAKSIMI = ASIAKKAITA + 1 };
static uint16_t portti;

static int kuormittaja(void *) {
    return kuormita(portti, ASIAKKAITA, KIERROKSIA) == 0 ? 0 : 1;
}

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(kuormittaja, nullptr);

    // @alku silmukka
    struct pollfd seuratut[MAKSIMI] = {{.fd = kuuntelija, .events = POLLIN}};
    yhteys tilat[MAKSIMI];               // tilat[i] vastaa seuratut[i]:tä
    int maara = 1, palveltu = 0, pyyntoja = 0;
    while (palveltu < ASIAKKAITA || maara > 1) {
        TARKISTA(poll(seuratut, (nfds_t)maara, -1));
        if (seuratut[0].revents & POLLIN && maara < MAKSIMI) {
            int fd = (int)TARKISTA(accept4(kuuntelija, nullptr, nullptr,
                                           SOCK_NONBLOCK));
            seuratut[maara] = (struct pollfd){.fd = fd, .events = POLLIN};
            tilat[maara++] = (yhteys){.fd = fd};
            palveltu++;
        }
        for (int i = 1; i < maara; i++) {
            if (seuratut[i].revents == 0) {
                continue;
            }
            yhteys *y = &tilat[i];
            ssize_t n = recv(y->fd, y->sisaan + y->n,
                             sizeof y->sisaan - y->n, 0);
            if (n == -1 && errno == EAGAIN) {
                continue;                // valeherätys: ei dataa
            }
            int k = 0;
            if (n > 0) {
                y->n += (size_t)n;
                k = kasittele_rivit(y);
            }
            if (n <= 0 || k < 0) {       // suljettu tai virhe: poista,
                close(y->fd);            // viimeinen siirtyy tilalle
                seuratut[i] = seuratut[--maara];
                tilat[i] = tilat[maara];
                i--;
                continue;
            }
            pyyntoja += k;
        }
    }
    // @loppu silmukka
    printf("poll: %d yhteyttä, %d pyyntöä\n", palveltu, pyyntoja);
    close(kuuntelija);
    return odota(pid);
}
