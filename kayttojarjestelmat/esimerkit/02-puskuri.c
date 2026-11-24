// stdio-puskuri kopioituu forkissa: rivi tulostuu kahdesti.
#define _GNU_SOURCE
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku puskuri
    printf("rivi ennen forkia\n");       // jää puskuriin (putki)
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {
        exit(0);                         // exit tyhjentää puskurin
    }
    TARKISTA(waitpid(pid, nullptr, 0));
    printf("vanhempi jatkaa\n");
    // @loppu puskuri
    return 0;
}
