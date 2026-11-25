#define _GNU_SOURCE
// Todellinen, tehollinen ja tallennettu käyttäjätunniste sekä
// oikeuksien tilapäinen ja pysyvä pudotus. Lapsiprosessi asetetaan
// samaan tilaan, jossa setuid-ohjelma käynnistyy.
#include <fcntl.h>

#include "kayttaja.h"

// @alku nayta
static const char *nimi(uid_t uid) {
    return uid == 0 ? "pääkäyttäjä" : "tavallinen";
}

static void nayta(const char *vaihe) {
    uid_t todellinen, tehollinen, tallennettu;
    TARKISTA(getresuid(&todellinen, &tehollinen, &tallennettu));
    printf("%s\n  todellinen %s, tehollinen %s, tallennettu %s\n", vaihe,
           nimi(todellinen), nimi(tehollinen), nimi(tallennettu));
}
// @loppu nayta

static const char *avaus(void) {
    int fd = open("salainen", O_RDONLY | O_CLOEXEC);
    const char *t = tulos(fd);
    if (fd != -1) {
        TARKISTA(close(fd));
    }
    return t;
}

// @alku setuid
static void setuid_ohjelma(void) {
    // Alkutila kuten setuid-ohjelmalla, jonka omistaa pääkäyttäjä ja
    // jonka tavallinen käyttäjä käynnisti.
    TARKISTA(setgroups(0, nullptr));
    TARKISTA(setresgid(TAVALLINEN_GID, TAVALLINEN_GID, TAVALLINEN_GID));
    TARKISTA(setresuid(TAVALLINEN_UID, 0, 0));
    nayta("käynnistys");
    printf("  avaus: %s, access: %s\n", avaus(),
           tulos(access("salainen", R_OK)));

    // Tilapäinen pudotus: tehollinen vaihtuu, tallennettu jää.
    TARKISTA(seteuid(getuid()));
    nayta("tilapäinen pudotus");
    printf("  avaus: %s\n", avaus());
    printf("  paluu pääkäyttäjäksi: %s\n", tulos(seteuid(0)));
    printf("  avaus: %s\n", avaus());

    // Pysyvä pudotus: pääkäyttäjän setuid asettaa kaikki kolme.
    TARKISTA(setuid(getuid()));
    nayta("pysyvä pudotus");
    printf("  paluu pääkäyttäjäksi: %s\n", tulos(seteuid(0)));
    printf("  avaus: %s\n", avaus());
}
// @loppu setuid

// @alku jarjestys
// Väärä järjestys: käyttäjä vaihdetaan ensin, jolloin oikeus vaihtaa
// ryhmää on jo mennyt ja pääkäyttäjän ryhmä jää voimaan.
static void vaara_jarjestys(void) {
    TARKISTA(setuid(TAVALLINEN_UID));
    printf("väärä järjestys\n  ryhmän vaihto käyttäjän jälkeen: %s\n",
           tulos(setgid(TAVALLINEN_GID)));
    printf("  ryhmä on yhä pääkäyttäjän: %s\n",
           getegid() == 0 ? "kyllä" : "ei");
}
// @loppu jarjestys

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

int main(void) {
    vaadi_paakayttaja();
    // Hakemisto, johon kaikilla on hakuoikeus, ja tiedosto, jonka vain
    // pääkäyttäjä saa lukea.
    TARKISTA(mkdir("hiekka", 0755));
    TARKISTA(chdir("hiekka"));
    int fd = (int)TARKISTA(open("salainen", O_CREAT | O_WRONLY | O_CLOEXEC,
                                0600));
    TARKISTA(close(fd));

    int koodi = lapsessa(setuid_ohjelma);
    koodi |= lapsessa(vaara_jarjestys);

    TARKISTA(unlink("salainen"));
    TARKISTA(chdir(".."));
    TARKISTA(rmdir("hiekka"));
    return koodi;
}
