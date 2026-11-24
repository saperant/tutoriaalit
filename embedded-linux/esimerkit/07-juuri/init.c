// Init pysyvältä, vain luku -tilaan kiinnitetyltä juurelta. Näyttää,
// miksi juurta ei voi muuttaa, ja tekee /etc-hakemistosta kirjoitettavan
// overlayfs:llä: muutokset menevät RAM-levylle, alkuperäinen säilyy.

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <unistd.h>

static void nayta_tiedosto(const char *otsikko, int hakemisto,
                           const char *nimi)
{
    char rivi[128] = "";
    int fd = openat(hakemisto, nimi, O_RDONLY);
    ssize_t n = fd < 0 ? -1 : read(fd, rivi, sizeof rivi - 1);
    if (fd >= 0) {
        close(fd);
    }
    if (n < 0) {
        printf("%s: %s\n", otsikko, strerror(errno));
        return;
    }
    rivi[n] = '\0';
    rivi[strcspn(rivi, "\n")] = '\0';
    printf("%s: %s\n", otsikko, rivi);
}

static void kirjoita(const char *polku, const char *sisalto)
{
    int fd = open(polku, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("kirjoitus %s: %s\n", polku, strerror(errno));
        return;
    }
    ssize_t n = write(fd, sisalto, strlen(sisalto));
    close(fd);
    printf("kirjoitus %s: %s\n", polku, n < 0 ? strerror(errno) : "ok");
}

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL);
    mount("tmpfs", "/run", "tmpfs", MS_NOSUID | MS_NODEV, "mode=0755");

    // @alku vainluku
    struct statvfs juuri;
    if (statvfs("/", &juuri) == 0) {
        printf("juuri: %s\n",
               (juuri.f_flag & ST_RDONLY) ? "vain luku" : "kirjoitettava");
    }
    kirjoita("/tila.txt", "kaynnistyksia=1\n");
    // @loppu vainluku

    // Hakemistokahva otetaan ennen overlayn kiinnittämistä: sen kautta
    // näkyy alempi kerros sellaisenaan myös kiinnityksen jälkeen.
    int alkuperainen = open("/etc", O_RDONLY | O_DIRECTORY);
    nayta_tiedosto("/etc/laite.conf", AT_FDCWD, "/etc/laite.conf");

    // @alku overlay
    mkdir("/run/etc", 0755);
    mkdir("/run/etc/yla", 0755);
    mkdir("/run/etc/tyo", 0755);
    const char *valinnat =
        "lowerdir=/etc,upperdir=/run/etc/yla,workdir=/run/etc/tyo";
    if (mount("overlay", "/etc", "overlay", 0, valinnat) != 0) {
        printf("overlay: %s\n", strerror(errno));
        return 1;
    }
    printf("overlay: /etc = /etc (alempi) + /run/etc/yla (ylempi)\n");
    kirjoita("/etc/laite.conf", "nimi=kentalla-muutettu\n");
    // @loppu overlay

    // @alku kerrokset
    nayta_tiedosto("yhdistetty", AT_FDCWD, "/etc/laite.conf");
    nayta_tiedosto("alempi    ", alkuperainen, "laite.conf");
    nayta_tiedosto("ylempi    ", AT_FDCWD, "/run/etc/yla/laite.conf");
    // @loppu kerrokset
    close(alkuperainen);

    umount("/etc");
    sync();
    reboot(RB_POWER_OFF);
    return 1;
}
