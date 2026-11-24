// Orpo prosessi siirtyy lähimmälle korjaajalle (subreaper).
#define _GNU_SOURCE
#include <sys/prctl.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku orpo
    TARKISTA(prctl(PR_SET_CHILD_SUBREAPER, 1));
    pid_t isovanhempi = getpid();
    int putki[2];
    TARKISTA(pipe(putki));

    fflush(stdout);
    pid_t lapsi = TARKISTA(fork());
    if (lapsi == 0) {
        if (TARKISTA(fork()) == 0) {     // lapsenlapsi
            close(putki[1]);
            char c;                      // odottaa, kunnes putki
            while (read(putki[0], &c, 1) > 0) {}   // suljetaan
            printf("lapsenlapsen vanhempi on nyt %s\n",
                   getppid() == isovanhempi ? "isovanhempi" : "muu");
            fflush(stdout);
            _exit(0);
        }
        _exit(0);                        // lapsi kuolee heti
    }
    TARKISTA(waitpid(lapsi, nullptr, 0));
    printf("lapsi korjattu, lapsenlapsi jäi orvoksi\n");
    fflush(stdout);
    close(putki[0]);
    close(putki[1]);                     // herättää lapsenlapsen
    pid_t korjattu = TARKISTA(wait(nullptr));
    printf("adoptoitu lapsenlapsi korjattu: %s\n",
           korjattu != lapsi ? "kyllä" : "ei");
    // @loppu orpo
    return 0;
}
