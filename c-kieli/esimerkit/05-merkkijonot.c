#include <stdio.h>
#include <string.h>

// @alku tunnus
// Kirjoittaa kohteeseen "nimi-nro". Palauttaa false, jos tulos ei
// mahtunut kokonaan (snprintf katkaisee ja päättää merkkijonon aina).
bool muodosta_tunnus(char *kohde, size_t koko, const char *nimi, int nro)
{
    int tarve = snprintf(kohde, koko, "%s-%d", nimi, nro);
    return tarve >= 0 && (size_t)tarve < koko;
}
// @loppu tunnus

int main(void)
{
    // @alku perusteet
    char tervehdys[] = "Hei";   // 4 tavua: 'H', 'e', 'i', '\0'
    printf("strlen = %zu, sizeof = %zu\n",
           strlen(tervehdys), sizeof tervehdys);

    tervehdys[0] = 'M';         // taulukkoa saa muuttaa
    printf("%s\n", tervehdys);

    const char *literaali = "vakio";   // literaalia ei saa muuttaa
    printf("%s, 3. merkki: %c\n", literaali, literaali[2]);
    // @loppu perusteet

    // @alku vertailu
    const char *a = "omena";
    char c[] = "omena";
    printf("a == c: %d\n", a == c);   // vertaa osoitteita!
    printf("strcmp(a, c) == 0: %d\n", strcmp(a, c) == 0);
    printf("\"apu\" < \"auto\": %d\n", strcmp("apu", "auto") < 0);
    // @loppu vertailu

    // @alku haku
    const char *polku = "/home/kayttaja/raportti.txt";
    const char *viimeinen = strrchr(polku, '/');
    const char *piste = strchr(polku, '.');
    printf("tiedosto: %s, pääte: %s\n", viimeinen + 1, piste + 1);
    bool loytyi = strstr(polku, "kayttaja") != nullptr;
    printf("sisältää 'kayttaja': %d\n", loytyi);
    // @loppu haku

    // @alku snprintf
    char puskuri[16];
    if (muodosta_tunnus(puskuri, sizeof puskuri, "tilaus", 2024)) {
        printf("'%s'\n", puskuri);
    }
    if (!muodosta_tunnus(puskuri, sizeof puskuri, "vuosiraportti", 2024)) {
        printf("katkaistu: '%s'\n", puskuri);
    }
    // @loppu snprintf
}
