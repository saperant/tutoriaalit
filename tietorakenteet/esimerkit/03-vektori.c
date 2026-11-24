// Dynaaminen taulukko (vektori): mittausnäytteiden puskuri, johon
// lisätään loppuun, poistetaan keskeltä ja josta luetaan indeksillä.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku rakenne
typedef struct {
    double *data;
    size_t koko;            // käytössä olevat alkiot
    size_t kapasiteetti;    // varattu tila, aina >= koko
} Vektori;

// Invariantti: kapasiteetti >= koko, ja data on nullptr vain, kun
// kapasiteetti on 0. Testit ja debug-käännökset tarkistavat sen.
static bool vektori_kunnossa(const Vektori *v)
{
    return v->koko <= v->kapasiteetti
           && (v->data != nullptr || v->kapasiteetti == 0);
}
// @loppu rakenne

// @alku lisaa
// Varmistaa tilan vähintään tarve-alkiolle. Kasvattaa kertoimella 1,5,
// jolloin kopioita on keskimäärin vakiomäärä alkiota kohti.
static bool vektori_varaa(Vektori *v, size_t tarve)
{
    if (tarve <= v->kapasiteetti) {
        return true;
    }
    size_t uusi = v->kapasiteetti + v->kapasiteetti / 2 + 8;
    if (uusi < tarve) {
        uusi = tarve;
    }
    double *data = realloc(v->data, uusi * sizeof *data);
    if (data == nullptr) {
        return false;           // v on ennallaan, mikään ei vuoda
    }
    v->data = data;
    v->kapasiteetti = uusi;
    return true;
}

static bool vektori_lisaa(Vektori *v, double arvo)
{
    if (!vektori_varaa(v, v->koko + 1)) {
        return false;
    }
    v->data[v->koko++] = arvo;
    return true;
}
// @loppu lisaa

// @alku poista
// Säilyttää järjestyksen: loppuosa siirretään, O(n).
static void vektori_poista(Vektori *v, size_t i)
{
    assert(i < v->koko);
    memmove(&v->data[i], &v->data[i + 1],
            (v->koko - i - 1) * sizeof *v->data);
    v->koko--;
}

// Järjestyksellä ei väliä: viimeinen siirretään aukkoon, O(1).
static void vektori_poista_vaihtamalla(Vektori *v, size_t i)
{
    assert(i < v->koko);
    v->data[i] = v->data[--v->koko];
}
// @loppu poista

static void tulosta(const char *otsikko, const Vektori *v)
{
    printf("%-22s", otsikko);
    for (size_t i = 0; i < v->koko; i++) {
        printf(" %.1f", v->data[i]);
    }
    printf("  [koko %zu/%zu]\n", v->koko, v->kapasiteetti);
}

int main(void)
{
    Vektori v = {nullptr, 0, 0};
    const double naytteet[] = {20.5, 21.0, -99.0, 21.4, 21.9, -99.0,
                               22.3};
    for (size_t i = 0; i < sizeof naytteet / sizeof naytteet[0]; i++) {
        if (!vektori_lisaa(&v, naytteet[i])) {
            free(v.data);
            return EXIT_FAILURE;
        }
    }
    assert(vektori_kunnossa(&v));
    tulosta("alussa:", &v);

    // Virheelliset näytteet (-99) pois; järjestys säilyy.
    for (size_t i = v.koko; i-- > 0;) {
        if (v.data[i] == -99.0) {
            vektori_poista(&v, i);
        }
    }
    tulosta("virheet poistettu:", &v);
    vektori_poista_vaihtamalla(&v, 0);
    tulosta("ensimmäinen vaihdettu:", &v);
    assert(vektori_kunnossa(&v));
    free(v.data);
    return EXIT_SUCCESS;
}
