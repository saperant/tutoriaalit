// Init, joka yrittää käynnistää joukon ohjelmia ja avata laitteita ja
// kertoo, mihin virheeseen kukin yritys päättyy. Tavallisimmat syyt
// siihen, ettei ohjelma käynnisty kohteessa, näkyvät virhekoodista.

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/wait.h>
#include <unistd.h>

// @alku kaynnista
// Käynnistää ohjelman lapsiprosessina. Jos execv epäonnistuu, lapsi
// tulostaa syyn; onnistunut ohjelma tulostaa itse.
static void kaynnista(const char *polku)
{
    printf("%-18s ", polku);
    fflush(stdout);
    pid_t lapsi = fork();
    if (lapsi == 0) {
        char *argumentit[] = { (char *)polku, NULL };
        execv(polku, argumentit);
        printf("execv: %s (%s)\n", strerror(errno),
               errno == ENOENT ? "ENOENT" :
               errno == ENOEXEC ? "ENOEXEC" :
               errno == EACCES ? "EACCES" : "muu");
        _exit(127);
    }
    waitpid(lapsi, NULL, 0);
}
// @loppu kaynnista

static void avaa(const char *polku)
{
    int fd = open(polku, O_RDWR | O_NONBLOCK);
    printf("%-18s open: %s\n", polku, fd < 0 ? strerror(errno) : "ok");
    if (fd >= 0) {
        close(fd);
    }
}

// Kopioi tiedoston ja tekee kopiosta ajettavan.
static void kopioi(const char *mista, const char *minne)
{
    char puskuri[4096];
    ssize_t n;
    int lahde = open(mista, O_RDONLY);
    int kohde = open(minne, O_WRONLY | O_CREAT | O_TRUNC, 0755);
    while (lahde >= 0 && kohde >= 0 &&
           (n = read(lahde, puskuri, sizeof puskuri)) > 0) {
        if (write(kohde, puskuri, (size_t)n) != n) {
            break;
        }
    }
    close(lahde);
    close(kohde);
}

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    mount("proc", "/proc", "proc", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    mount("tmpfs", "/run", "tmpfs", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL);
    kopioi("/bin/staattinen", "/run/kopio");
    mknod("/dev/anturi0", S_IFCHR | 0600, makedev(240, 0));

    // @alku yritykset
    kaynnista("/bin/staattinen");
    kaynnista("/bin/dynaaminen");
    kaynnista("/bin/isanta");
    kaynnista("/bin/skripti");
    kaynnista("/bin/oikeudeton");
    kaynnista("/run/kopio");
    kaynnista("/bin/puuttuu");
    avaa("/dev/ttyAMA0");
    avaa("/dev/ttyAMA1");
    avaa("/dev/anturi0");
    // @loppu yritykset

    sync();
    reboot(RB_POWER_OFF);
    return 1;
}
