// Luvun 9 esimerkkien yhteiset apufunktiot: pääkäyttäjän oikeuksien
// varmistus ja pysyvä pudotus tavalliseksi käyttäjäksi.
#ifndef KAYTTAJA_H
#define KAYTTAJA_H

#include <grp.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

// Ydin tuntee käyttäjän vain numerona, eikä numeron tarvitse löytyä
// tiedostosta /etc/passwd. 65534 on perinteinen "nobody": tunniste,
// joka ei omista mitään.
enum { TAVALLINEN_UID = 65534, TAVALLINEN_GID = 65534 };

// @alku pudotus
// Pysyvä pudotus: ensin lisäryhmät, sitten ryhmä ja viimeisenä
// käyttäjä. Väärässä järjestyksessä oikeus vaihtaa ryhmää menisi
// käyttäjän mukana, ja pääkäyttäjän ryhmät jäisivät voimaan.
static inline void pudota_oikeudet(void) {
    TARKISTA(setgroups(0, nullptr));
    TARKISTA(setgid(TAVALLINEN_GID));
    TARKISTA(setuid(TAVALLINEN_UID));
}
// @loppu pudotus

// @alku sudo
// Tunnisteiden vaihto vaatii pääkäyttäjän oikeudet. Tavallisena
// käyttäjänä käynnistetty esimerkki käynnistää itsensä uudelleen
// sudolla; -n kieltää salasanan kysymisen.
static inline void vaadi_paakayttaja(void) {
    if (geteuid() == 0) {
        return;
    }
    char polku[4096];
    ssize_t n = TARKISTA(readlink("/proc/self/exe", polku,
                                  sizeof polku - 1));
    polku[n] = '\0';
    execlp("sudo", "sudo", "-n", "--", polku, (char *)nullptr);
    fprintf(stderr, "esimerkki tarvitsee pääkäyttäjän oikeudet "
                    "(sudo tai kehityskontti)\n");
    exit(EXIT_FAILURE);
}
// @loppu sudo

// Odottaa lasta ja palauttaa sen paluuarvon (tai -signaalin).
static inline int odota_lasta(pid_t lapsi) {
    int tila = 0;
    TARKISTA(waitpid(lapsi, &tila, 0));
    return WIFEXITED(tila) ? WEXITSTATUS(tila) : -WTERMSIG(tila);
}

// Virhekoodin nimi tai "onnistui"; errno luetaan heti kutsun jälkeen.
static inline const char *tulos(long paluuarvo) {
    return paluuarvo == -1 ? strerrorname_np(errno) : "onnistui";
}

#endif
