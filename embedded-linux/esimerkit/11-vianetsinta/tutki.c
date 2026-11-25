// Init vianetsinnän esimerkkiin: ajaa anturipalvelun viallisella
// asetustiedostolla, ottaa kaatumisesta talteen ytimen lokirivit ja
// ohjaa ydinvedoksen datalevylle, josta se luetaan isännällä.

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

static void kirjoita(const char *polku, const char *arvo)
{
    int fd = open(polku, O_WRONLY);
    if (fd < 0 || write(fd, arvo, strlen(arvo)) < 0) {
        printf("tutki: %s: %s\n", polku, strerror(errno));
    }
    if (fd >= 0) {
        close(fd);
    }
}

// @alku loki
// Näyttää ytimen lokista ohjelmaa koskevan rivin ja rekisterivedoksen
// pc-rivin. Prosessin numero korvataan pisteillä.
static void nayta_loki(int kmsg, const char *nimi)
{
    char tietue[512];
    ssize_t n;
    size_t pituus = strlen(nimi);
    while ((n = read(kmsg, tietue, sizeof tietue - 1)) > 0) {
        tietue[n] = '\0';
        char *viesti = strchr(tietue, ';');
        if (viesti == NULL) {
            continue;
        }
        viesti++;
        viesti[strcspn(viesti, "\n")] = '\0';
        if (strncmp(viesti, nimi, pituus) == 0 && viesti[pituus] == '[') {
            char *loppu = strchr(viesti, ']');
            printf("loki: %s[..]%s\n", nimi, loppu ? loppu + 1 : "");
        } else if (strncmp(viesti, "pc : ", 5) == 0) {
            printf("loki: %s\n", viesti);
        }
    }
}
// @loppu loki

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    mount("proc", "/proc", "proc", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    if (mount("/dev/vda", "/data", "ext4", 0, NULL) != 0) {
        printf("tutki: /data: %s\n", strerror(errno));
    }

    // @alku asetukset
    // Ydin kirjaa käyttäjätilan kaatumiset lokiin ja kirjoittaa
    // ydinvedoksen datalevylle ohjelman nimellä (%e).
    kirjoita("/proc/sys/debug/exception-trace", "1");
    kirjoita("/proc/sys/kernel/core_pattern", "/data/core.%e");
    struct rlimit rajaton = { RLIM_INFINITY, RLIM_INFINITY };
    setrlimit(RLIMIT_CORE, &rajaton);   // periytyy palvelulle
    // @loppu asetukset

    int kmsg = open("/dev/kmsg", O_RDONLY | O_NONBLOCK);
    lseek(kmsg, 0, SEEK_END);

    // @alku aja
    pid_t lapsi = fork();
    if (lapsi == 0) {
        execl("/bin/anturi", "anturi", "/etc/rikki.conf", (char *)NULL);
        _exit(127);
    }
    int tila = 0;
    waitpid(lapsi, &tila, 0);
    if (WIFSIGNALED(tila)) {
        printf("tutki: anturi kuoli signaaliin %d (%s)%s\n",
               WTERMSIG(tila), strsignal(WTERMSIG(tila)),
               WCOREDUMP(tila) ? ", ydinvedos kirjoitettu" : "");
    } else {
        printf("tutki: anturi paattyi, paluuarvo %d\n", WEXITSTATUS(tila));
    }
    // @loppu aja
    nayta_loki(kmsg, "anturi");

    struct stat st;
    printf("tutki: /data/core.anturi %s\n",
           stat("/data/core.anturi", &st) == 0 ? "on" : "puuttuu");
    umount("/data");
    sync();
    reboot(RB_POWER_OFF);
    return 1;
}
