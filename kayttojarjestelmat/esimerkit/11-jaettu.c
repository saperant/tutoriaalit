// POSIX-jaettu muisti: shm_open + mmap. Prosessit kasvattavat samaa
// laskuria, ja prosessien välinen semafori suojaa kriittisen alueen.
#define _GNU_SOURCE
#include <fcntl.h>
#include <semaphore.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

// @alku rakenne
typedef struct {
    sem_t lukko;                         // pshared = 1
    long laskuri;
} jaettu_t;
// @loppu rakenne

enum { PROSESSEJA = 4, KIERROKSIA = 10'000 };

int main(void) {
    // @alku luo
    char nimi[64];                       // ainutkertainen nimi
    snprintf(nimi, sizeof nimi, "/kj-jaettu-%d", (int)getpid());
    int fd = TARKISTA(shm_open(nimi, O_RDWR | O_CREAT | O_EXCL, 0600));
    TARKISTA(shm_unlink(nimi));          // nimi pois heti, muisti jää
    TARKISTA(ftruncate(fd, sizeof(jaettu_t)));
    jaettu_t *j = TARKISTA_MAP(mmap(nullptr, sizeof *j,
                                    PROT_READ | PROT_WRITE, MAP_SHARED,
                                    fd, 0));
    TARKISTA(close(fd));                 // kartoitus säilyy
    TARKISTA(sem_init(&j->lukko, 1, 1));
    // @loppu luo

    // @alku kayta
    pid_t lapset[PROSESSEJA];
    for (int i = 0; i < PROSESSEJA; i++) {
        lapset[i] = TARKISTA(fork());
        if (lapset[i] == 0) {
            for (int k = 0; k < KIERROKSIA; k++) {
                while (sem_wait(&j->lukko) == -1 && errno == EINTR) {}
                j->laskuri++;            // kriittinen alue
                sem_post(&j->lukko);
            }
            _exit(0);
        }
    }
    for (int i = 0; i < PROSESSEJA; i++) {
        TARKISTA(waitpid(lapset[i], nullptr, 0));
    }
    printf("laskuri: %ld (odotettu %d)\n", j->laskuri,
           PROSESSEJA * KIERROKSIA);
    sem_destroy(&j->lukko);
    TARKISTA(munmap(j, sizeof *j));
    // @loppu kayta
    return 0;
}
