// Pienin hyödyllinen init: ydin käynnistää tämän ohjelman prosessina 1.
// Se kiinnittää ytimen virtuaaliset tiedostojärjestelmät, kertoo mihin
// järjestelmään se heräsi ja sammuttaa koneen siististi.

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <unistd.h>

// @alku kiinnita
// Luo liitoskohdan tarvittaessa ja kiinnittää tiedostojärjestelmän.
static int kiinnita(const char *lahde, const char *kohde,
                    const char *tyyppi, unsigned long liput)
{
    if (mkdir(kohde, 0755) != 0 && errno != EEXIST) {
        fprintf(stderr, "init: mkdir %s: %s\n", kohde, strerror(errno));
        return -1;
    }
    if (mount(lahde, kohde, tyyppi, liput, NULL) != 0) {
        fprintf(stderr, "init: mount %s: %s\n", kohde, strerror(errno));
        return -1;
    }
    printf("init: kiinnitetty %-5s (%s)\n", kohde, tyyppi);
    return 0;
}
// @loppu kiinnita

// Tulostaa tiedoston ensimmäisen rivin otsikon kanssa.
static void nayta_rivi(const char *otsikko, const char *polku)
{
    char rivi[256];
    FILE *f = fopen(polku, "r");
    if (f == NULL || fgets(rivi, sizeof rivi, f) == NULL) {
        printf("init: %s: ei luettavissa\n", otsikko);
    } else {
        rivi[strcspn(rivi, "\n")] = '\0';
        printf("init: %s: %s\n", otsikko, rivi);
    }
    if (f != NULL) {
        fclose(f);
    }
}

static const char *loytyyko(const char *polku)
{
    struct stat st;
    return stat(polku, &st) == 0 ? "on" : "ei";
}

// @alku main
int main(void)
{
    // Konsoli on sarjaportti: rivipuskurointi pitää tulosteen järjestyksessä.
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (getpid() != 1) {
        fprintf(stderr, "init: ajettava prosessina 1\n");
        return 1;
    }
    printf("init: PID %d, vanhempi %d\n", (int)getpid(), (int)getppid());

    const unsigned long turva = MS_NOSUID | MS_NODEV | MS_NOEXEC;
    kiinnita("proc", "/proc", "proc", turva);
    kiinnita("sysfs", "/sys", "sysfs", turva);
    kiinnita("devtmpfs", "/dev", "devtmpfs", MS_NOSUID | MS_NOEXEC);
    kiinnita("tmpfs", "/run", "tmpfs", turva);

    struct utsname u;
    if (uname(&u) == 0) {
        printf("init: ydin %s, arkkitehtuuri %s\n", u.release, u.machine);
    }
    nayta_rivi("komentorivi", "/proc/cmdline");
    nayta_rivi("prosessorit", "/sys/devices/system/cpu/online");
    printf("init: /dev/ttyAMA0 %s, /dev/vda %s\n",
           loytyyko("/dev/ttyAMA0"), loytyyko("/dev/vda"));

    // PID 1 ei saa päättyä: ydin pysähtyisi paniikkiin. Sammutetaan.
    printf("init: sammutetaan\n");
    sync();
    reboot(RB_POWER_OFF);
    fprintf(stderr, "init: reboot: %s\n", strerror(errno));
    return 1;
}
// @loppu main
