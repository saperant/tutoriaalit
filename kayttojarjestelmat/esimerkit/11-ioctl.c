// ioctl: laitekohtaiset komennot, joita read ja write eivät kata.
// Esimerkkeinä putken puskurin täyttö ja pseudopäätteen ikkunan koko.
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku fionread
    int putki[2];
    TARKISTA(pipe(putki));
    TARKISTA(write(putki[1], "12345", 5));
    int odottaa;
    TARKISTA(ioctl(putki[0], FIONREAD, &odottaa));
    printf("putkessa odottaa %d tavua\n", odottaa);
    printf("putki on pääte: %s\n", isatty(putki[0]) ? "kyllä" : "ei");
    // @loppu fionread

    // @alku pty
    int isanta = TARKISTA(posix_openpt(O_RDWR | O_NOCTTY));
    TARKISTA(grantpt(isanta));
    TARKISTA(unlockpt(isanta));
    int orja = TARKISTA(open(ptsname(isanta), O_RDWR | O_NOCTTY));
    printf("pseudopäätteen orja on pääte: %s\n",
           isatty(orja) ? "kyllä" : "ei");

    struct winsize koko = {.ws_row = 24, .ws_col = 80};
    TARKISTA(ioctl(isanta, TIOCSWINSZ, &koko));  // pääteohjelma asettaa
    struct winsize luettu;
    TARKISTA(ioctl(orja, TIOCGWINSZ, &luettu));  // sovellus kysyy
    printf("ikkunan koko: %u riviä, %u saraketta\n", luettu.ws_row,
           luettu.ws_col);

    struct termios asetukset;            // tcgetattr on ioctl:n kääre
    TARKISTA(tcgetattr(orja, &asetukset));
    printf("kaiutus päällä: %s, kanoninen tila: %s\n",
           asetukset.c_lflag & ECHO ? "kyllä" : "ei",
           asetukset.c_lflag & ICANON ? "kyllä" : "ei");
    // @loppu pty

    // @alku tyhja
    if (ioctl(putki[0], TIOCGWINSZ, &luettu) == -1) {
        printf("TIOCGWINSZ putkelle: %s\n", strerrorname_np(errno));
    }
    // @loppu tyhja
    close(orja);
    close(isanta);
    close(putki[0]);
    close(putki[1]);
    return 0;
}
