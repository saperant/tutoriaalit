// Yksi rakenne, monta tyyppiä: sama kasvava taulukko kahdella tavalla.
// 1) void * ja alkion koko: yksi käännetty toteutus kaikille tyypeille.
// 2) Makro, joka tuottaa tyyppikohtaisen toteutuksen.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku void
// Alkiot ovat tavuja: rakenne tietää vain alkion koon.
typedef struct {
    void *data;
    size_t alkion_koko, koko, kapasiteetti;
} Vektori;

static bool vektori_lisaa(Vektori *v, const void *alkio)
{
    if (v->koko == v->kapasiteetti) {
        size_t uusi = v->kapasiteetti ? 2 * v->kapasiteetti : 4;
        void *p = realloc(v->data, uusi * v->alkion_koko);
        if (p == nullptr) {
            return false;
        }
        v->data = p;
        v->kapasiteetti = uusi;
    }
    memcpy((char *)v->data + v->koko * v->alkion_koko, alkio,
           v->alkion_koko);
    v->koko++;
    return true;
}

// Kutsuja muuntaa osoittimen oikeaan tyyppiin; kääntäjä ei tarkista.
static void *vektori_hae(const Vektori *v, size_t i)
{
    return (char *)v->data + i * v->alkion_koko;
}
// @loppu void

// @alku makro
// Makro tuottaa tyypin ja funktiot annetulle alkiotyypille. Kääntäjä
// tarkistaa tyypit, ja jokainen tyyppi saa oman konekoodinsa.
#define VEKTORI_MAARITTELE(Nimi, Tyyppi)                                  \
    typedef struct {                                                      \
        Tyyppi *data;                                                     \
        size_t koko, kapasiteetti;                                        \
    } Nimi;                                                               \
    static bool Nimi##_lisaa(Nimi *v, Tyyppi alkio)                       \
    {                                                                     \
        if (v->koko == v->kapasiteetti) {                                 \
            size_t uusi = v->kapasiteetti ? 2 * v->kapasiteetti : 4;      \
            Tyyppi *p = realloc(v->data, uusi * sizeof *p);               \
            if (p == nullptr) {                                           \
                return false;                                             \
            }                                                             \
            v->data = p;                                                  \
            v->kapasiteetti = uusi;                                       \
        }                                                                 \
        v->data[v->koko++] = alkio;                                       \
        return true;                                                      \
    }

VEKTORI_MAARITTELE(LukuVektori, double)
// @loppu makro

typedef struct {
    char nimi[12];
    int portti;
} Palvelu;

// @alku vertailu
// Järjestys annetaan funktio-osoittimena, kuten qsortille.
static int portin_mukaan(const void *a, const void *b)
{
    const Palvelu *x = a, *y = b;
    return (x->portti > y->portti) - (x->portti < y->portti);
}
// @loppu vertailu

int main(void)
{
    // @alku kaytto
    Vektori palvelut = {.alkion_koko = sizeof(Palvelu)};
    const Palvelu lisattavat[] = {
        {"https", 443}, {"ssh", 22}, {"dns", 53}, {"http", 80}, {"ntp", 123},
    };
    bool ok = true;
    for (size_t i = 0; i < sizeof lisattavat / sizeof lisattavat[0]; i++) {
        ok &= vektori_lisaa(&palvelut, &lisattavat[i]);
    }
    qsort(palvelut.data, palvelut.koko, sizeof(Palvelu), portin_mukaan);
    for (size_t i = 0; ok && i < palvelut.koko; i++) {
        const Palvelu *p = vektori_hae(&palvelut, i);
        printf("%-6s %4d\n", p->nimi, p->portti);
    }

    LukuVektori luvut = {};
    for (int i = 1; i <= 5; i++) {
        ok &= LukuVektori_lisaa(&luvut, i * 0.5);
    }
    // LukuVektori_lisaa(&luvut, "puoli");   // ei käänny: väärä tyyppi
    double summa = 0;
    for (size_t i = 0; ok && i < luvut.koko; i++) {
        summa += luvut.data[i];
    }
    printf("lukuja %zu, summa %.1f\n", luvut.koko, summa);
    // @loppu kaytto
    free(palvelut.data);
    free(luvut.data);
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
