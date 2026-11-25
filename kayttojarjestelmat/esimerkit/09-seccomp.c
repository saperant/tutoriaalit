#define _GNU_SOURCE
// Järjestelmäkutsujen rajaus seccomp-suodattimella: prosessi luopuu
// itse kutsusta, jota se ei tarvitse, eikä saa sitä enää takaisin.
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <stddef.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <sys/syscall.h>

#include "kayttaja.h"

#if defined(__x86_64__)
#define ARKKITEHTUURI AUDIT_ARCH_X86_64
#elif defined(__aarch64__)
#define ARKKITEHTUURI AUDIT_ARCH_AARCH64
#else
#error "lisää arkkitehtuurin AUDIT_ARCH-vakio"
#endif

// @alku suodatin
// Suodatin on pieni BPF-ohjelma, jonka ydin ajaa jokaisen
// järjestelmäkutsun alussa. Se näkee kutsun numeron ja argumentit
// (struct seccomp_data) ja palauttaa päätöksen.
static void kiella_soketit(void) {
    struct sock_filter ohjelma[] = {
        // Väärä arkkitehtuuri: lopeta prosessi (numerot eroavat).
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                 offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, ARKKITEHTUURI, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        // socket-kutsu palauttaa virheen EPERM, muut sallitaan.
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                 offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_socket, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog suodatin = {
        .len = sizeof ohjelma / sizeof ohjelma[0],
        .filter = ohjelma,
    };
    // Ilman tätä lippua suodattimen asennus vaatisi pääkäyttäjän:
    // muuten sillä voisi hämätä setuid-ohjelmaa.
    TARKISTA(prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0));
    TARKISTA(prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &suodatin));
}
// @loppu suodatin

static const char *soketti(void) {
    int fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    const char *t = tulos(fd);
    if (fd != -1) {
        TARKISTA(close(fd));
    }
    return t;
}

// @alku main
int main(void) {
    printf("ennen suodatinta: socket %s\n", soketti());
    kiella_soketit();
    printf("suodattimen jälkeen: socket %s\n", soketti());
    printf("muut kutsut toimivat: getpid %s\n",
           getpid() > 0 ? "onnistui" : "epäonnistui");

    fflush(stdout);
    pid_t lapsi = (pid_t)TARKISTA(fork());
    if (lapsi == 0) {
        printf("lapsi peri suodattimen: socket %s\n", soketti());
        fflush(stdout);
        _exit(0);
    }
    return odota_lasta(lapsi);
}
// @loppu main
