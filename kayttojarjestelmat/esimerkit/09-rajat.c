#define _GNU_SOURCE
// Resurssirajat: pehmeä raja on voimassa oleva, kova raja katto, jota
// tavallinen prosessi voi vain laskea.
#include <fcntl.h>
#include <signal.h>
#include <sys/resource.h>

#include "kayttaja.h"

static void kokeet(void) {
    // @alku koko
    // Raja ylittyessä ydin lähettää signaalin SIGXFSZ, joka oletuksena
    // lopettaa prosessin. Kun se ohitetaan, write palauttaa virheen.
    signal(SIGXFSZ, SIG_IGN);
    struct rlimit raja = {.rlim_cur = 4096, .rlim_max = 8192};
    TARKISTA(setrlimit(RLIMIT_FSIZE, &raja));

    static const char data[6000] = {0};
    int fd = (int)TARKISTA(open("iso", O_CREAT | O_WRONLY | O_CLOEXEC,
                                0600));
    ssize_t n = write(fd, data, sizeof data);
    printf("pehmeä raja 4096: kirjoitettiin %zd / %zu tavua\n", n,
           sizeof data);
    printf("seuraava kirjoitus: %s\n", tulos(write(fd, data, 1)));
    // @loppu koko

    // @alku kova
    raja.rlim_cur = 8192;       // pehmeän saa nostaa kovaan asti
    printf("pehmeä kovan tasolle: %s\n",
           tulos(setrlimit(RLIMIT_FSIZE, &raja)));
    raja.rlim_cur = 16384;      // muttei sen yli
    printf("pehmeä kovan yli: %s\n",
           tulos(setrlimit(RLIMIT_FSIZE, &raja)));
    raja.rlim_cur = 8192;
    raja.rlim_max = 16384;      // kovaa ei saa nostaa lainkaan
    printf("kovan nosto: %s\n", tulos(setrlimit(RLIMIT_FSIZE, &raja)));
    // @loppu kova

    // @alku periytyy
    fflush(stdout);
    pid_t lapsi = (pid_t)TARKISTA(fork());
    if (lapsi == 0) {
        TARKISTA(getrlimit(RLIMIT_FSIZE, &raja));
        printf("lapsen rajat: pehmeä %llu, kova %llu\n",
               (unsigned long long)raja.rlim_cur,
               (unsigned long long)raja.rlim_max);
        fflush(stdout);
        _exit(0);
    }
    odota_lasta(lapsi);
    // @loppu periytyy

    TARKISTA(close(fd));
    TARKISTA(unlink("iso"));
}

int main(void) {
    // Pääkäyttäjä saa nostaa kovia rajoja (CAP_SYS_RESOURCE), joten
    // kokeet ajetaan tavallisena käyttäjänä omassa hakemistossa.
    TARKISTA(mkdir("hiekka", 0700));
    if (geteuid() == 0) {
        TARKISTA(chown("hiekka", TAVALLINEN_UID, TAVALLINEN_GID));
    }
    TARKISTA(chdir("hiekka"));
    fflush(stdout);
    pid_t lapsi = (pid_t)TARKISTA(fork());
    if (lapsi == 0) {
        if (geteuid() == 0) {
            pudota_oikeudet();
        }
        kokeet();
        fflush(stdout);
        _exit(0);
    }
    int koodi = odota_lasta(lapsi);
    TARKISTA(chdir(".."));
    TARKISTA(rmdir("hiekka"));
    return koodi;
}
