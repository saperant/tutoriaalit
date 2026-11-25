#define _GNU_SOURCE
// Kyvyt (capabilities): pääkäyttäjän oikeudet paloina. Tavallinen
// käyttäjä, jolle jätetään vain CAP_KILL, saa lähettää signaalin
// toisen käyttäjän prosessille mutta ei mitään muuta.
#include <fcntl.h>
#include <linux/capability.h>
#include <signal.h>
#include <sys/prctl.h>
#include <sys/syscall.h>

#include "kayttaja.h"

// @alku joukot
// glibc ei tarjoa kääreitä kutsuille capget ja capset (ne ovat
// libcap-kirjastossa), joten kutsut tehdään suoraan. Versio 3 kuvaa
// 64 kykyä kahdella 32-bittisellä sanalla.
static struct __user_cap_header_struct otsake = {
    .version = _LINUX_CAPABILITY_VERSION_3,
};

static bool tehollinen(int kyky) {
    struct __user_cap_data_struct data[2] = {};
    TARKISTA(syscall(SYS_capget, &otsake, data));
    return (data[kyky / 32].effective >> (kyky % 32)) & 1;
}

static void jata_vain(int kyky) {
    struct __user_cap_data_struct data[2] = {};
    data[kyky / 32].permitted = 1u << (kyky % 32);
    data[kyky / 32].effective = 1u << (kyky % 32);
    TARKISTA(syscall(SYS_capset, &otsake, data));
}
// @loppu joukot

static const char *avaus(void) {
    int fd = open("salainen", O_RDONLY | O_CLOEXEC);
    const char *t = tulos(fd);
    if (fd != -1) {
        TARKISTA(close(fd));
    }
    return t;
}

static void nayta(const char *kuka) {
    printf("%s\n  CAP_KILL: %s, CAP_DAC_OVERRIDE: %s\n", kuka,
           tehollinen(CAP_KILL) ? "on" : "ei",
           tehollinen(CAP_DAC_OVERRIDE) ? "on" : "ei");
    printf("  signaali pääkäyttäjän prosessille: %s\n",
           tulos(kill(getppid(), 0)));
    printf("  pääkäyttäjän tiedoston avaus: %s\n", avaus());
}

// @alku lapset
static void ilman_kykyja(void) {
    pudota_oikeudet();      // tunnisteen vaihto tyhjentää kyvyt
    nayta("tavallinen käyttäjä");
}

static void yksi_kyky(void) {
    // Kyvyt säilyvät tunnisteen vaihdon yli sallitussa joukossa, ja
    // niistä jätetään voimaan yksi.
    TARKISTA(prctl(PR_SET_KEEPCAPS, 1));
    pudota_oikeudet();
    jata_vain(CAP_KILL);
    nayta("tavallinen käyttäjä, jolla on CAP_KILL");
}
// @loppu lapset

static int lapsessa(void (*koe)(void)) {
    fflush(stdout);
    pid_t lapsi = (pid_t)TARKISTA(fork());
    if (lapsi == 0) {
        koe();
        fflush(stdout);
        _exit(0);
    }
    return odota_lasta(lapsi);
}

static void paakayttaja(void) {
    nayta("pääkäyttäjä");
}

int main(void) {
    vaadi_paakayttaja();
    TARKISTA(mkdir("hiekka", 0755));
    TARKISTA(chdir("hiekka"));
    int fd = (int)TARKISTA(open("salainen", O_CREAT | O_WRONLY | O_CLOEXEC,
                                0600));
    TARKISTA(close(fd));

    int koodi = lapsessa(paakayttaja);
    koodi |= lapsessa(ilman_kykyja);
    koodi |= lapsessa(yksi_kyky);

    TARKISTA(unlink("salainen"));
    TARKISTA(chdir(".."));
    TARKISTA(rmdir("hiekka"));
    return koodi;
}
