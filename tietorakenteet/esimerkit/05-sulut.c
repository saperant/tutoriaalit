// Pino: tarkistetaan, ovatko sulkeet konfiguraatiotiedoston riveillä
// tasapainossa. Viimeksi avattu sulje suljetaan ensin – juuri pinon
// LIFO-järjestys (last in, first out).
#include <stdio.h>
#include <string.h>

enum { SYVYYS = 64 };

// @alku pino
typedef struct {
    char merkki[SYVYYS];
    size_t paikka[SYVYYS];
    size_t koko;
} Pino;

static bool pino_lisaa(Pino *p, char merkki, size_t paikka)
{
    if (p->koko == SYVYYS) {
        return false;               // ylivuoto: liian syvä sisäkkäisyys
    }
    p->merkki[p->koko] = merkki;
    p->paikka[p->koko] = paikka;
    p->koko++;
    return true;
}
// @loppu pino

// @alku tarkista
// Palauttaa -1, jos rivi on kunnossa, muuten virheen sarakkeen.
static long tarkista(const char *rivi)
{
    Pino p = {.koko = 0};
    for (size_t i = 0; rivi[i] != '\0'; i++) {
        char c = rivi[i];
        // Silmukka päättyy ennen nollamerkkiä, joten strchr ei löydä
        // merkkijonojen loppumerkkiä.
        const char *avaava = strchr("([{", c);
        const char *sulkeva = strchr(")]}", c);
        if (avaava != nullptr) {
            if (!pino_lisaa(&p, c, i)) {
                return (long)i;
            }
        } else if (sulkeva != nullptr) {
            char odotettu = "([{"[sulkeva - ")]}"];
            if (p.koko == 0 || p.merkki[p.koko - 1] != odotettu) {
                return (long)i;
            }
            p.koko--;               // pinon päällimmäinen pois
        }
    }
    return p.koko == 0 ? -1 : (long)p.paikka[p.koko - 1];
}
// @loppu tarkista

int main(void)
{
    const char *rivit[] = {
        "palvelin { portit = [80, 443]; aika = (10 * 60); }",
        "lista = [1, 2, (3, 4]]",
        "lohko { avain = [1, 2] ",
        "arvo = 5) + 2",
    };
    for (size_t i = 0; i < sizeof rivit / sizeof rivit[0]; i++) {
        long virhe = tarkista(rivit[i]);
        if (virhe < 0) {
            printf("rivi %zu: kunnossa\n", i + 1);
        } else {
            printf("rivi %zu: virhe sarakkeessa %ld\n", i + 1, virhe + 1);
        }
    }
    return 0;
}
