#define _GNU_SOURCE
// Tiedosto-oikeuksien tarkistus: mikä luokka valitaan, mitä hakemiston
// bitit tarkoittavat, umask sekä virheet EACCES ja EPERM.
#include <dirent.h>
#include <fcntl.h>

#include "kayttaja.h"

// Luo tiedoston annetuilla oikeusbiteillä (umaskista riippumatta).
static void luo(const char *polku, mode_t tila) {
    int fd = (int)TARKISTA(open(polku, O_CREAT | O_WRONLY | O_CLOEXEC,
                                0600));
    TARKISTA(fchmod(fd, tila));
    TARKISTA(close(fd));
}

// @alku kokeile
// Yrittää avata tiedoston ja palauttaa tuloksen nimen.
static const char *avaus(const char *polku, int liput) {
    int fd = open(polku, liput | O_CLOEXEC);
    const char *t = tulos(fd);
    if (fd != -1) {
        TARKISTA(close(fd));
    }
    return t;
}
// @loppu kokeile

static void kokeet(void) {
    // @alku luokka
    printf("== tiedoston bitit, omistajan avaus\n");
    luo("t", 0000);
    printf("0000  luku: %s\n", avaus("t", O_RDONLY));
    TARKISTA(chmod("t", 0004));    // vain "muut" saavat lukea
    printf("0004  luku: %s\n", avaus("t", O_RDONLY));
    TARKISTA(chmod("t", 0400));
    printf("0400  luku: %s, kirjoitus: %s\n", avaus("t", O_RDONLY),
           avaus("t", O_WRONLY));
    // @loppu luokka

    // @alku umask
    printf("== umask\n");
    umask(027);
    int fd = (int)TARKISTA(open("u", O_CREAT | O_WRONLY | O_CLOEXEC,
                                0666));
    struct stat st;
    TARKISTA(fstat(fd, &st));
    TARKISTA(close(fd));
    printf("pyydetty 0666, umask 027: tila %04o\n",
           (unsigned)(st.st_mode & 07777));
    // @loppu umask

    // @alku hakemisto
    printf("== hakemiston bitit\n");
    TARKISTA(mkdir("h", 0700));
    luo("h/a", 0444);
    TARKISTA(chmod("h", 0600));    // ei hakuoikeutta (x)
    printf("0600  avaus nimellä: %s\n", avaus("h/a", O_RDONLY));
    TARKISTA(chmod("h", 0300));    // ei lukuoikeutta (r)
    DIR *d = opendir("h");
    printf("0300  avaus nimellä: %s, listaus: %s\n",
           avaus("h/a", O_RDONLY), d ? "onnistui" : strerrorname_np(errno));
    TARKISTA(chmod("h", 0500));    // ei kirjoitusoikeutta (w)
    printf("0500  poisto: %s\n", tulos(unlink("h/a")));
    TARKISTA(chmod("h", 0700));
    printf("0700  poisto: %s (tiedoston tila oli 0444)\n",
           tulos(unlink("h/a")));
    // @loppu hakemisto

    // @alku eperm
    printf("== EACCES ja EPERM\n");
    printf("oman tiedoston lahjoitus pääkäyttäjälle: %s\n",
           tulos(chown("t", 0, (gid_t)-1)));
    printf("vaihto pääkäyttäjäksi: %s\n", tulos(setuid(0)));
    // @loppu eperm

    TARKISTA(unlink("t"));
    TARKISTA(unlink("u"));
    TARKISTA(rmdir("h"));
}

// @alku main
int main(void) {
    // Pääkäyttäjä ohittaa oikeusbitit, joten kokeet ajetaan tavallisena
    // käyttäjänä omassa hakemistossa.
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
// @loppu main
