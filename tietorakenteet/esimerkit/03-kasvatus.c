// Dynaamisen taulukon kasvatusstrategiat: kun tila loppuu, varataan
// uusi taulukko ja vanhat alkiot kopioidaan. Lasketaan kopioiden
// määrä, kun taulukkoon lisätään n alkiota yksi kerrallaan.
#include <stddef.h>
#include <stdio.h>

typedef size_t (*Kasvatus)(size_t vanha);

// @alku strategiat
static size_t yksi_kerrallaan(size_t vanha) { return vanha + 1; }
static size_t vakiolisays(size_t vanha) { return vanha + 64; }
static size_t puolitoista(size_t vanha) { return vanha + vanha / 2 + 1; }
static size_t tuplaus(size_t vanha) { return vanha ? 2 * vanha : 1; }
// @loppu strategiat

// @alku malli
typedef struct {
    unsigned long long kopioita;    // alkioita siirretty vanhasta uuteen
    unsigned long long varauksia;   // kasvatuskertoja
    size_t kapasiteetti;            // lopullinen kapasiteetti
} Tulos;

static Tulos lisaa_n(size_t n, Kasvatus kasvata)
{
    Tulos t = {0, 0, 0};
    size_t koko = 0;
    for (size_t i = 0; i < n; i++) {
        if (koko == t.kapasiteetti) {
            t.kapasiteetti = kasvata(t.kapasiteetti);
            t.kopioita += koko;     // realloc kopioi vanhat alkiot
            t.varauksia++;
        }
        koko++;
    }
    return t;
}
// @loppu malli

int main(void)
{
    const size_t n = 100000;
    struct {
        const char *nimi;
        Kasvatus kasvata;
    } strategiat[] = {
        {"+1", yksi_kerrallaan},
        {"+64", vakiolisays},
        {"x1.5", puolitoista},
        {"x2", tuplaus},
    };
    printf("%-6s %12s %10s %10s %9s\n", "kasvu", "kopioita",
           "kopio/alk.", "varauksia", "hukka-%");
    for (size_t s = 0; s < sizeof strategiat / sizeof strategiat[0];
         s++) {
        Tulos t = lisaa_n(n, strategiat[s].kasvata);
        double hukka = 100.0 * (double)(t.kapasiteetti - n)
                       / (double)t.kapasiteetti;
        printf("%-6s %12llu %10.2f %10llu %9.1f\n", strategiat[s].nimi,
               t.kopioita, (double)t.kopioita / (double)n, t.varauksia,
               hukka);
    }
    return 0;
}
