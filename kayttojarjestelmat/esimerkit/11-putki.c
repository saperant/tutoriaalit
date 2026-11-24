// Putki kahden prosessin välillä: lapsi muuttaa rivit isoiksi
// kirjaimiksi. Tiedoston loppu tulee, kun kaikki kirjoituspäät on
// suljettu; suljettuun putkeen kirjoittaminen antaa EPIPE-virheen.
#define _GNU_SOURCE
#include <ctype.h>
#include <limits.h>
#include <signal.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku putket
    int sinne[2], takaisin[2];           // [0] luku, [1] kirjoitus
    TARKISTA(pipe(sinne));
    TARKISTA(pipe(takaisin));
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {
        close(sinne[1]);                 // muuten EOF ei tule koskaan
        close(takaisin[0]);
        char c;
        while (read(sinne[0], &c, 1) == 1) {
            c = (char)toupper((unsigned char)c);
            TARKISTA(write(takaisin[1], &c, 1));
        }
        _exit(0);                        // EOF: vanhempi sulki putken
    }
    close(sinne[0]);
    close(takaisin[1]);
    const char viesti[] = "putki on tavuvirta\nilman viestirajoja\n";
    TARKISTA(write(sinne[1], viesti, sizeof viesti - 1));
    close(sinne[1]);                     // lapselle tiedoston loppu

    char vastaus[128];
    size_t n = 0;
    for (ssize_t k; (k = read(takaisin[0], vastaus + n,
                              sizeof vastaus - 1 - n)) > 0;) {
        n += (size_t)k;
    }
    vastaus[n] = '\0';
    printf("%s", vastaus);
    close(takaisin[0]);
    TARKISTA(waitpid(pid, nullptr, 0));
    // @loppu putket

    // @alku epipe
    int p[2];
    TARKISTA(pipe(p));
    close(p[0]);                         // ei yhtään lukijaa
    signal(SIGPIPE, SIG_IGN);            // muuten prosessi kuolisi
    if (write(p[1], "x", 1) == -1) {
        printf("kirjoitus ilman lukijaa: %s\n", strerrorname_np(errno));
    }
    close(p[1]);
    printf("PIPE_BUF = %d: enintään näin suuri kirjoitus on atominen\n",
           PIPE_BUF);
    // @loppu epipe
    return 0;
}
