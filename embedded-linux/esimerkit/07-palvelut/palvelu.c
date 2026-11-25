// Esimerkkipalvelu init-järjestelmän testaamiseen. Käytös valitaan
// argumentilla, jotta yksi ohjelma riittää kaikkiin tapauksiin:
//
//   palvelu NIMI vakaa             valmis heti, päättyy SIGTERMiin
//   palvelu NIMI kaatuva N         kaatuu N ensimmäistä kertaa
//   palvelu NIMI jumittuva         ei välitä SIGTERMistä
//
// Valmiudesta ilmoitetaan luomalla tiedosto /run/valmis/NIMI.

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static volatile sig_atomic_t lopeta = 0;

static void kasittele_term(int signaali)
{
    (void)signaali;
    lopeta = 1;
}

// @alku valmis
// Valmiusilmoitus: tiedosto, jota init odottaa. Systemd käyttää samaan
// tarkoitukseen sd_notify-viestiä (READY=1) UNIX-soketin kautta.
static int ilmoita_valmis(const char *nimi)
{
    char polku[128];
    snprintf(polku, sizeof polku, "/run/valmis/%s", nimi);
    int fd = open(polku, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (fd < 0) {
        fprintf(stderr, "%s: %s: %s\n", nimi, polku, strerror(errno));
        return -1;
    }
    return close(fd);
}
// @loppu valmis

// Laskee käynnistyskerrat tiedostoon /run/NIMI.kerrat.
static int kasvata_laskuria(const char *nimi)
{
    char polku[128];
    snprintf(polku, sizeof polku, "/run/%s.kerrat", nimi);
    int kerrat = 0;
    FILE *f = fopen(polku, "r");
    if (f != NULL) {
        if (fscanf(f, "%d", &kerrat) != 1) {
            kerrat = 0;
        }
        fclose(f);
    }
    kerrat++;
    f = fopen(polku, "w");
    if (f != NULL) {
        fprintf(f, "%d\n", kerrat);
        fclose(f);
    }
    return kerrat;
}

// @alku odota
// Odottaa SIGTERMiä ilman kilpatilannetta: signaali estetään ennen
// valmiusilmoitusta, ja sigsuspend vapauttaa sen vasta odottaessaan.
static void odota_lopetusta(const char *nimi)
{
    sigset_t esto, vanha;
    sigemptyset(&esto);
    sigaddset(&esto, SIGTERM);
    sigprocmask(SIG_BLOCK, &esto, &vanha);
    struct sigaction sa = {.sa_handler = kasittele_term};
    sigaction(SIGTERM, &sa, NULL);
    if (ilmoita_valmis(nimi) != 0) {
        exit(1);
    }
    while (!lopeta) {
        sigsuspend(&vanha);
    }
    printf("%s: SIGTERM, tila tallennettu\n", nimi);
    exit(0);
}
// @loppu odota

int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (argc < 3) {
        fprintf(stderr, "kaytto: palvelu NIMI vakaa|kaatuva N|jumittuva\n");
        return 2;
    }
    const char *nimi = argv[1];
    const char *tapa = argv[2];
    if (strcmp(tapa, "vakaa") == 0) {
        odota_lopetusta(nimi);
    } else if (strcmp(tapa, "kaatuva") == 0 && argc == 4) {
        // @alku kaatuva
        int kerta = kasvata_laskuria(nimi);
        if (kerta <= atoi(argv[3])) {
            printf("%s: anturi ei vastaa (yritys %d)\n", nimi, kerta);
            return 3;
        }
        odota_lopetusta(nimi);
        // @loppu kaatuva
    } else if (strcmp(tapa, "jumittuva") == 0) {
        signal(SIGTERM, SIG_IGN);
        if (ilmoita_valmis(nimi) != 0) {
            return 1;
        }
        for (;;) {
            pause();
        }
    }
    fprintf(stderr, "%s: tuntematon tapa %s\n", nimi, tapa);
    return 2;
}
