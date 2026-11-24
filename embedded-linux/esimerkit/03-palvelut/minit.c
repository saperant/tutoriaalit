// minit: pieni init-järjestelmä. Lukee palveluluettelon, käynnistää
// palvelut järjestyksessä, odottaa kunkin valmiutta, käynnistää kaatuneen
// palvelun uudelleen rajatun määrän kertoja ja sammuttaa järjestelmän
// pysäyttämällä palvelut käänteisessä järjestyksessä.

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

enum { MAKS_PALVELUT = 8, MAKS_ARGIT = 8 };

// @alku palvelu
struct palvelu {
    char nimi[32];
    int uudelleen_maks;  // sallitut uudelleenkäynnistykset
    int uudelleen;       // tehdyt uudelleenkäynnistykset
    char *argv[MAKS_ARGIT + 1];
    pid_t pid;           // 0, kun palvelu ei ole käynnissä
    const char *tila;
};
// @loppu palvelu

static struct palvelu palvelut[MAKS_PALVELUT];
static int palveluja = 0;

static void kiinnita(const char *lahde, const char *kohde, const char *tyyppi)
{
    mkdir(kohde, 0755);
    if (mount(lahde, kohde, tyyppi, MS_NOSUID | MS_NOEXEC, NULL) != 0) {
        fprintf(stderr, "minit: mount %s: %s\n", kohde, strerror(errno));
    }
}

static void nuku_ms(long ms)
{
    struct timespec t = {ms / 1000, (ms % 1000) * 1000000L};
    nanosleep(&t, NULL);
}

// @alku asetukset
// Rivi: NIMI UUDELLEEN OHJELMA [ARGUMENTIT...]; '#' aloittaa kommentin.
static int lue_asetukset(const char *polku)
{
    FILE *f = fopen(polku, "r");
    if (f == NULL) {
        fprintf(stderr, "minit: %s: %s\n", polku, strerror(errno));
        return -1;
    }
    char rivi[256];
    while (fgets(rivi, sizeof rivi, f) != NULL && palveluja < MAKS_PALVELUT) {
        rivi[strcspn(rivi, "#\n")] = '\0';
        char *nimi = strtok(rivi, " \t");
        char *uudelleen = strtok(NULL, " \t");
        if (nimi == NULL || uudelleen == NULL) {
            continue;
        }
        struct palvelu *p = &palvelut[palveluja];
        snprintf(p->nimi, sizeof p->nimi, "%s", nimi);
        p->uudelleen_maks = atoi(uudelleen);
        int n = 0;
        for (char *s; n < MAKS_ARGIT && (s = strtok(NULL, " \t")); n++) {
            p->argv[n] = strdup(s);
        }
        if (n > 0) {
            palveluja++;
        }
    }
    fclose(f);
    return 0;
}
// @loppu asetukset

static void kaynnista(struct palvelu *p)
{
    pid_t pid = fork();
    if (pid == 0) {
        setsid();  // oma istunto: palvelu ei saa konsolin signaaleja
        execv(p->argv[0], p->argv);
        fprintf(stderr, "minit: exec %s: %s\n", p->argv[0], strerror(errno));
        _exit(127);
    }
    p->pid = pid;
}

static int valmis(const struct palvelu *p)
{
    char polku[64];
    snprintf(polku, sizeof polku, "/run/valmis/%.31s", p->nimi);
    return access(polku, F_OK) == 0;
}

// @alku odota
// Käynnistää palvelun ja odottaa sen valmiutta enintään 5 sekuntia.
// Ennen valmiutta kaatunut palvelu käynnistetään uudelleen, jos
// uudelleenkäynnistyksiä on jäljellä.
static void kaynnista_ja_odota(struct palvelu *p)
{
    printf("minit: kaynnistetaan %s\n", p->nimi);
    kaynnista(p);
    for (int odotettu = 0; odotettu < 5000; odotettu += 10) {
        if (valmis(p)) {
            p->tila = "kaynnissa";
            printf("minit: %s valmis\n", p->nimi);
            return;
        }
        int status;
        if (waitpid(p->pid, &status, WNOHANG) == p->pid) {
            p->pid = 0;
            int koodi = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
            if (p->uudelleen >= p->uudelleen_maks) {
                printf("minit: %s paattyi (%d), ei uudelleenkaynnistysta\n",
                       p->nimi, koodi);
                p->tila = "epaonnistui";
                return;
            }
            p->uudelleen++;
            printf("minit: %s paattyi (%d), uudelleen %d/%d\n", p->nimi,
                   koodi, p->uudelleen, p->uudelleen_maks);
            nuku_ms(100L << p->uudelleen);  // kasvava viive
            kaynnista(p);
        }
        nuku_ms(10);
    }
    p->tila = "ei valmis";
    printf("minit: %s ei ilmoittanut valmiutta\n", p->nimi);
}
// @loppu odota

// @alku pysayta
// SIGTERM, sekunnin odotus ja tarvittaessa SIGKILL.
static void pysayta(struct palvelu *p)
{
    if (p->pid == 0) {
        return;
    }
    kill(p->pid, SIGTERM);
    for (int odotettu = 0; odotettu < 1000; odotettu += 10) {
        if (waitpid(p->pid, NULL, WNOHANG) == p->pid) {
            printf("minit: %s pysaytetty\n", p->nimi);
            p->pid = 0;
            return;
        }
        nuku_ms(10);
    }
    printf("minit: %s ei paattynyt, SIGKILL\n", p->nimi);
    kill(p->pid, SIGKILL);
    waitpid(p->pid, NULL, 0);
    p->pid = 0;
}
// @loppu pysayta

// @alku main
int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (getpid() != 1) {
        fprintf(stderr, "minit: ajettava prosessina 1\n");
        return 1;
    }
    kiinnita("proc", "/proc", "proc");
    kiinnita("sysfs", "/sys", "sysfs");
    kiinnita("devtmpfs", "/dev", "devtmpfs");
    kiinnita("tmpfs", "/run", "tmpfs");
    mkdir("/run/valmis", 0755);

    if (lue_asetukset("/etc/palvelut.conf") == 0) {
        for (int i = 0; i < palveluja; i++) {
            kaynnista_ja_odota(&palvelut[i]);
        }
    }
    printf("minit: %-8s %-12s %s\n", "palvelu", "tila", "uudelleen");
    for (int i = 0; i < palveluja; i++) {
        printf("minit: %-8s %-12s %d\n", palvelut[i].nimi, palvelut[i].tila,
               palvelut[i].uudelleen);
    }

    printf("minit: sammutetaan\n");
    for (int i = palveluja - 1; i >= 0; i--) {
        pysayta(&palvelut[i]);
    }
    sync();
    reboot(RB_POWER_OFF);
    return 1;
}
// @loppu main
