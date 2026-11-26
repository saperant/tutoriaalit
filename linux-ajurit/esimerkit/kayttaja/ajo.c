// Testijärjestelmän init: lukee tiedoston /vaiheet ja suorittaa sen
// komennot yksi kerrallaan, tulostaa kunkin komennon ja sen tuloksen sekä
// ne ytimen lokin rivit, jotka komento sai aikaan. Lopuksi kone
// sammutetaan. BusyBoxia ei tarvita: jokainen komento on muutama rivi C:tä.
//
// Komennot (yksi rivillä, # aloittaa kommentin; rivit "# @alku osa" ja
// "# @loppu osa" kopioidaan tulosteeseen, jotta tekstiin voi poimia osan):
//   suodata etuliite...   ytimen lokista näytetään vain nämä rivit
//                         (~ etuliitteessä tarkoittaa välilyöntiä)
//   lataa moduuli.ko [parametrit]   finit_module (/lib/modules/)
//   poista nimi           delete_module
//   kirjoita polku teksti kirjoittaa tekstin tiedostoon
//   lue polku [teksti]    tulostaa tiedoston (tekstin sisältävät) rivit
//   listaa hakemisto      tulostaa hakemiston nimet aakkosjärjestyksessä
//   aja ohjelma [arg...]  käynnistää ohjelman ja odottaa sen päättymistä
//   nuku millisekunnit    odottaa

#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

enum { MAKS_SANAT = 16, MAKS_SUODATTIMET = 16 };

static int kmsg = -1;
static char suodattimet[MAKS_SUODATTIMET][64];
static int suodatinmaara;

// @alku loki
// /dev/kmsg antaa ytimen lokin tietue kerrallaan muodossa
// "taso,järjestysnumero,aika,liput;viesti". Ajat ja järjestysnumerot
// vaihtelevat, joten tulostetaan vain suodattimiin täsmäävät viestit.
// Viestin muut kuin tulostettavat ASCII-merkit, myös sisäiset
// rivinvaihdot, ovat muodossa \xHH; reunojen rivinvaihdot poistetaan.
static void nayta_loki(void)
{
    char tietue[1024];
    ssize_t n;
    while ((n = read(kmsg, tietue, sizeof tietue - 1)) > 0) {
        tietue[n] = '\0';
        char *viesti = strchr(tietue, ';');
        if (viesti == NULL) {
            continue;
        }
        viesti++;
        viesti[strcspn(viesti, "\n")] = '\0';
        while (strncmp(viesti, "\\x0a", 4) == 0) {
            viesti += 4;
        }
        size_t pituus = strlen(viesti);
        while (pituus >= 4 && strcmp(viesti + pituus - 4, "\\x0a") == 0) {
            viesti[pituus -= 4] = '\0';
        }
        for (int i = 0; i < suodatinmaara; i++) {
            if (strncmp(viesti, suodattimet[i],
                        strlen(suodattimet[i])) == 0) {
                printf("  loki: %s\n", viesti);
                break;
            }
        }
    }
}
// @loppu loki

static int lue_tiedosto(const char *polku, char *puskuri, size_t koko)
{
    int fd = open(polku, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }
    size_t kaytetty = 0;
    ssize_t n;
    while (kaytetty < koko - 1 &&
           (n = read(fd, puskuri + kaytetty, koko - 1 - kaytetty)) > 0) {
        kaytetty += (size_t)n;
    }
    close(fd);
    puskuri[kaytetty] = '\0';
    return (int)kaytetty;
}

static void nuku(long millisekunnit)
{
    struct timespec t = {millisekunnit / 1000,
                         (millisekunnit % 1000) * 1000000L};
    nanosleep(&t, NULL);
}

// @alku lataa
static void lataa(char **sanat, int maara)
{
    char polku[128];
    char parametrit[256] = "";
    size_t kaytetty = 0;
    snprintf(polku, sizeof polku, "/lib/modules/%s", sanat[1]);
    // Parametrit välitetään ytimelle yhtenä merkkijonona: "a=1 b=2".
    for (int i = 2; i < maara && kaytetty < sizeof parametrit; i++) {
        kaytetty += (size_t)snprintf(parametrit + kaytetty,
                                     sizeof parametrit - kaytetty, "%s%s",
                                     i > 2 ? " " : "", sanat[i]);
    }
    int fd = open(polku, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        printf("  virhe: %s: %s\n", polku, strerror(errno));
        return;
    }
    if (syscall(SYS_finit_module, fd, parametrit, 0) != 0) {
        printf("  virhe: %s\n", strerror(errno));
    }
    close(fd);
    // Uusi ajuri voi käynnistää lykättyjä sidontoja, jotka ydin ajaa
    // työjonossa latauksen jälkeen. Odotetaan, että niiden lokirivit
    // ehtivät tämän komennon tulosteeseen.
    nuku(200);
}

static void poista(const char *nimi)
{
    if (syscall(SYS_delete_module, nimi, O_NONBLOCK) != 0) {
        printf("  virhe: %s\n", strerror(errno));
    }
}
// @loppu lataa

static void kirjoita(const char *polku, const char *teksti)
{
    int fd = open(polku, O_WRONLY | O_CLOEXEC);
    if (fd < 0) {
        printf("  virhe: %s: %s\n", polku, strerror(errno));
        return;
    }
    if (write(fd, teksti, strlen(teksti)) < 0) {
        printf("  virhe: %s\n", strerror(errno));
    }
    close(fd);
}

static void lue(const char *polku, const char *suodatin)
{
    char sisalto[4096];
    if (lue_tiedosto(polku, sisalto, sizeof sisalto) < 0) {
        printf("  virhe: %s: %s\n", polku, strerror(errno));
        return;
    }
    for (char *rivi = strtok(sisalto, "\n"); rivi != NULL;
         rivi = strtok(NULL, "\n")) {
        if (suodatin == NULL || strstr(rivi, suodatin) != NULL) {
            printf("  %s\n", rivi);
        }
    }
}

static int vertaa(const void *a, const void *b)
{
    return strcmp(*(char *const *)a, *(char *const *)b);
}

static void listaa(const char *hakemisto)
{
    DIR *d = opendir(hakemisto);
    if (d == NULL) {
        printf("  virhe: %s: %s\n", hakemisto, strerror(errno));
        return;
    }
    char *nimet[256];
    int maara = 0;
    struct dirent *e;
    while ((e = readdir(d)) != NULL && maara < 256) {
        if (e->d_name[0] != '.') {
            nimet[maara++] = strdup(e->d_name);
        }
    }
    closedir(d);
    qsort(nimet, (size_t)maara, sizeof nimet[0], vertaa);
    for (int i = 0; i < maara; i++) {
        printf("  %s\n", nimet[i]);
        free(nimet[i]);
    }
}

// @alku aja
static void aja(char **sanat)
{
    fflush(stdout);
    pid_t lapsi = fork();
    if (lapsi == 0) {
        execv(sanat[1], &sanat[1]);
        printf("  virhe: %s: %s\n", sanat[1], strerror(errno));
        _exit(127);
    }
    int tila;
    waitpid(lapsi, &tila, 0);
    if (WIFSIGNALED(tila)) {
        printf("  signaali %s\n", sigabbrev_np(WTERMSIG(tila)));
    } else if (WEXITSTATUS(tila) != 0) {
        printf("  paluuarvo %d\n", WEXITSTATUS(tila));
    }
}
// @loppu aja

static void suorita(char *rivi)
{
    char *sanat[MAKS_SANAT + 1];
    int maara = 0;
    // kirjoita-komennon teksti on rivin loppu välilyönteineen. strtok
    // katkaisi sen, joten katkaisukohta palautetaan välilyönniksi.
    for (char *s = strtok(rivi, " "); s != NULL && maara < MAKS_SANAT;
         s = strtok(NULL, " ")) {
        sanat[maara++] = s;
        if (maara == 3 && strcmp(sanat[0], "kirjoita") == 0) {
            char *loppu = strtok(NULL, "");
            if (loppu != NULL) {
                loppu[-1] = ' ';
            }
            break;
        }
    }
    sanat[maara] = NULL;
    if (maara == 0) {
        return;
    }
    const char *k = sanat[0];
    if (strcmp(k, "suodata") == 0) {
        for (int i = 1; i < maara && suodatinmaara < MAKS_SUODATTIMET;
             i++) {
            char *s = suodattimet[suodatinmaara++];
            snprintf(s, sizeof suodattimet[0], "%s", sanat[i]);
            for (; *s != '\0'; s++) {
                *s = *s == '~' ? ' ' : *s;  // ~ on välilyönti
            }
        }
        return;  // ei tulosteta
    }
    printf("# %s", k);
    for (int i = 1; i < maara; i++) {
        printf(" %s", sanat[i]);
    }
    printf("\n");
    if (strcmp(k, "lataa") == 0 && maara >= 2) {
        lataa(sanat, maara);
    } else if (strcmp(k, "poista") == 0 && maara == 2) {
        poista(sanat[1]);
    } else if (strcmp(k, "kirjoita") == 0 && maara == 3) {
        kirjoita(sanat[1], sanat[2]);
    } else if (strcmp(k, "lue") == 0 && (maara == 2 || maara == 3)) {
        lue(sanat[1], sanat[2]);
    } else if (strcmp(k, "listaa") == 0 && maara == 2) {
        listaa(sanat[1]);
    } else if (strcmp(k, "aja") == 0 && maara >= 2) {
        aja(sanat);
    } else if (strcmp(k, "nuku") == 0 && maara == 2) {
        nuku(atol(sanat[1]));
    } else {
        printf("  virhe: tuntematon komento\n");
    }
    fflush(stdout);
    nayta_loki();
}

// @alku main
int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    mount("proc", "/proc", "proc", 0, NULL);
    mount("sysfs", "/sys", "sysfs", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    mount("debugfs", "/sys/kernel/debug", "debugfs", 0, NULL);
    mount("tracefs", "/sys/kernel/tracing", "tracefs", 0, NULL);
    kmsg = open("/dev/kmsg", O_RDONLY | O_NONBLOCK | O_CLOEXEC);
    lseek(kmsg, 0, SEEK_END);  // vain tästä eteenpäin tulevat rivit

    static char vaiheet[16384];
    if (lue_tiedosto("/vaiheet", vaiheet, sizeof vaiheet) < 0) {
        printf("init: /vaiheet puuttuu\n");
    }
    char *seuraava = vaiheet;
    while (*seuraava != '\0') {
        char *rivi = seuraava;
        size_t pituus = strcspn(rivi, "\n");
        seuraava = rivi[pituus] == '\n' ? rivi + pituus + 1 : rivi + pituus;
        rivi[pituus] = '\0';
        if (strncmp(rivi, "# @", 3) == 0) {
            printf("%s\n", rivi);  // osamerkintä tulosteeseen tekstiä varten
        } else if (rivi[0] != '#') {
            suorita(rivi);
        }
    }
    sync();
    reboot(RB_POWER_OFF);
    return 1;
}
// @loppu main
