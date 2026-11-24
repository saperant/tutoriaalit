// seccomp-suodatin: prosessi rajaa itse, mitä järjestelmäkutsuja se ja
// sen lapset saavat tehdä. Konttiajoympäristöt asettavat vastaavan
// suodattimen jokaiselle kontille (Dockerin oletusprofiili estää
// noin 50 kutsua).
#define _GNU_SOURCE        // syscall()
#include <errno.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <signal.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <unistd.h>

// @alku suodatin
// BPF-ohjelma tarkastelee kutsun numeroa ja arkkitehtuuria.
#define SALLI     BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
#define KIELLA(k, toimi) \
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, (k), 0, 1), \
    BPF_STMT(BPF_RET | BPF_K, (toimi))

static int asenna(unsigned int kielletty, unsigned int toimi)
{
    struct sock_filter ohjelma[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                 offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                 offsetof(struct seccomp_data, nr)),
        KIELLA(kielletty, toimi),
        SALLI,
    };
    struct sock_fprog prog = {
        .len = sizeof ohjelma / sizeof ohjelma[0],
        .filter = ohjelma,
    };
    // Ilman tätä vain root saisi asentaa suodattimen: lippu takaa, ettei
    // prosessi voi enää saada lisäoikeuksia (esim. setuid-ohjelmalla).
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0)
        return -1;
    return (int)syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog);
}
// @loppu suodatin

int main(void)
{
    // @alku virhe
    // Lapsi 1: mkdir palauttaa virheen EPERM, muut kutsut toimivat.
    pid_t lapsi = fork();
    if (lapsi == 0) {
        if (asenna(SYS_mkdir, SECCOMP_RET_ERRNO | EPERM) != 0)
            _exit(2);
        int tulos = mkdir("/tmp/ei-saa-luoda", 0700);
        printf("mkdir: %d (%s)\n", tulos, strerror(errno));
        printf("getpid toimii yhä: %s\n", getpid() > 0 ? "kyllä" : "ei");
        fflush(stdout);
        _exit(0);
    }
    int tila;
    waitpid(lapsi, &tila, 0);
    // @loppu virhe

    // @alku tappo
    // Lapsi 2: uname tappaa prosessin signaalilla SIGSYS.
    fflush(stdout);
    lapsi = fork();
    if (lapsi == 0) {
        if (asenna(SYS_uname, SECCOMP_RET_KILL_PROCESS) != 0)
            _exit(2);
        struct utsname u;
        uname(&u);
        _exit(0);                       // tänne ei päästä
    }
    waitpid(lapsi, &tila, 0);
    if (WIFSIGNALED(tila))
        printf("uname: prosessi tapettiin signaalilla %s\n",
               WTERMSIG(tila) == SIGSYS ? "SIGSYS" : "muu");
    // @loppu tappo
    return 0;
}
