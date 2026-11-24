// exec korvaa prosessin ohjelman; paluuarvo kertoo, miten lapsi
// päättyi.
#define _GNU_SOURCE
#include <signal.h>
#include <spawn.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

extern char **environ;

static void kerro(const char *nimi, int tila) {
    if (WIFEXITED(tila)) {
        printf("%s: päättyi, koodi %d\n", nimi, WEXITSTATUS(tila));
    } else if (WIFSIGNALED(tila)) {
        printf("%s: signaali SIG%s\n", nimi,
               sigabbrev_np(WTERMSIG(tila)));
    }
}

int main(void) {
    int tila;
    // @alku exec
    fflush(stdout);
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {
        char *argv[] = {"sh", "-c", "echo \"sh sai argumentin $1\"",
                        "sh", "hei", nullptr};
        execvp("sh", argv);
        _exit(127);                      // vain, jos exec epäonnistui
    }
    TARKISTA(waitpid(pid, &tila, 0));
    kerro("sh", tila);
    // @loppu exec

    // @alku virhe
    fflush(stdout);
    pid = TARKISTA(fork());
    if (pid == 0) {
        char *argv[] = {"ei-tallaista", nullptr};
        execvp(argv[0], argv);
        printf("exec epäonnistui: %s\n", strerrorname_np(errno));
        fflush(stdout);
        _exit(127);
    }
    TARKISTA(waitpid(pid, &tila, 0));
    kerro("ei-tallaista", tila);
    // @loppu virhe

    // @alku tapettu
    pid = TARKISTA(fork());
    if (pid == 0) {
        for (;;) {
            pause();
        }
    }
    TARKISTA(kill(pid, SIGKILL));
    TARKISTA(waitpid(pid, &tila, 0));
    kerro("pause", tila);
    // @loppu tapettu

    // @alku spawn
    fflush(stdout);
    char *argv[] = {"sh", "-c", "exit 3", nullptr};
    int virhe = posix_spawnp(&pid, "sh", nullptr, nullptr, argv,
                             environ);
    if (virhe != 0) {
        printf("posix_spawnp: %s\n", strerror(virhe));
        return 1;
    }
    TARKISTA(waitpid(pid, &tila, 0));
    kerro("posix_spawnp", tila);
    // @loppu spawn
    return 0;
}
