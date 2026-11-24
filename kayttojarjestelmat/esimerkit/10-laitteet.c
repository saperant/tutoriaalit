// Merkkilaitteet /dev-hakemistossa: laitetiedoston tyyppi ja
// laitenumerot sekä laitteiden erikoiskäytös luettaessa ja kirjoitettaessa.
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku numerot
    const char *laitteet[] = {"/dev/null", "/dev/zero", "/dev/full",
                              "/dev/urandom"};
    for (int i = 0; i < 4; i++) {
        struct stat s;
        TARKISTA(stat(laitteet[i], &s));
        printf("%-13s %s, pää %u, ali %u\n", laitteet[i],
               S_ISCHR(s.st_mode) ? "merkkilaite" :
               S_ISBLK(s.st_mode) ? "lohkolaite" : "muu",
               major(s.st_rdev), minor(s.st_rdev));
    }
    // @loppu numerot

    // @alku kaytos
    char puskuri[16];
    int fd = TARKISTA(open("/dev/null", O_RDWR));
    printf("null: kirjoitus %zd, luku %zd (tiedoston loppu)\n",
           write(fd, "roskaa", 6), read(fd, puskuri, sizeof puskuri));
    TARKISTA(close(fd));

    fd = TARKISTA(open("/dev/zero", O_RDONLY));
    memset(puskuri, 'x', sizeof puskuri);
    ssize_t n = TARKISTA(read(fd, puskuri, sizeof puskuri));
    int nollia = 0;
    for (ssize_t i = 0; i < n; i++) {
        nollia += puskuri[i] == 0;
    }
    printf("zero: luettiin %zd tavua, nollia %d\n", n, nollia);
    TARKISTA(close(fd));

    fd = TARKISTA(open("/dev/full", O_WRONLY));
    if (write(fd, "x", 1) == -1) {
        printf("full: kirjoitus epäonnistui, %s\n",
               strerrorname_np(errno));
    }
    TARKISTA(close(fd));
    // @loppu kaytos
    return 0;
}
