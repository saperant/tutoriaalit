// Pikaoppaan idiomit yhdessä ohjelmassa.
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct solmu {
    int avain;
    struct solmu *seuraava;
} Solmu;

// @alku linkki
// Poisto listasta ilman erikoistapausta.
static void poista(Solmu **p, int avain)
{
    while (*p != nullptr && (*p)->avain != avain) {
        p = &(*p)->seuraava;
    }
    if (*p != nullptr) {
        Solmu *pois = *p;
        *p = pois->seuraava;
        free(pois);
    }
}
// @loppu linkki

// @alku kasvu
// Dynaaminen taulukko: kasvu kertoimella, realloc väliaikaiseen.
static bool varaa(int **data, size_t *kap, size_t tarve)
{
    if (tarve <= *kap) {
        return true;
    }
    size_t uusi = *kap + *kap / 2 + 8 > tarve ? *kap + *kap / 2 + 8 : tarve;
    int *d = realloc(*data, uusi * sizeof *d);
    if (d == nullptr) {
        return false;               // *data ennallaan
    }
    *data = d;
    *kap = uusi;
    return true;
}
// @loppu kasvu

// @alku indeksit
// Rengas: koko kahden potenssi, indeksit juoksevat vapaasti.
#define RENGAS_TAYTTO(kirj, luettu) ((uint32_t)((kirj) - (luettu)))
#define RENGAS_PAIKKA(i, koko) ((i) & ((koko) - 1))
// Binäärikeko taulukossa.
#define VANHEMPI(i) (((i) - 1) / 2)
#define VASEN(i) (2 * (i) + 1)
#define OIKEA(i) (2 * (i) + 2)
// Tunkeileva lista: tietue jäsenen osoitteesta.
#define SISALTAVA(p, tyyppi, jasen) \
    ((tyyppi *)((char *)(p) - offsetof(tyyppi, jasen)))
// @loppu indeksit

// @alku fnv
static uint32_t fnv1a(const char *s)
{
    uint32_t h = 2166136261u;
    while (*s != '\0') {
        h ^= (unsigned char)*s++;
        h *= 16777619u;
    }
    return h;
}
// @loppu fnv

typedef struct {
    int tunniste;
    Solmu linkki;
} Tehtava;

int main(void)
{
    Solmu *lista = nullptr;
    for (int i = 3; i > 0; i--) {
        Solmu *s = malloc(sizeof *s);
        if (s == nullptr) {
            return EXIT_FAILURE;
        }
        *s = (Solmu){i, lista};
        lista = s;
    }
    poista(&lista, 1);
    printf("lista: %d %d\n", lista->avain, lista->seuraava->avain);
    while (lista != nullptr) {
        Solmu *s = lista;
        lista = s->seuraava;
        free(s);
    }

    int *data = nullptr;
    size_t kap = 0;
    if (!varaa(&data, &kap, 100)) {
        return EXIT_FAILURE;
    }
    printf("kapasiteetti %zu\n", kap);
    free(data);

    printf("rengas: täyttö %u, paikka %u\n",
           RENGAS_TAYTTO(2u, UINT32_MAX - 1), RENGAS_PAIKKA(13u, 8u));
    printf("keko: vanhempi(5)=%d vasen(2)=%d oikea(2)=%d\n", VANHEMPI(5),
           VASEN(2), OIKEA(2));
    Tehtava t = {7, {0, nullptr}};
    printf("tunkeileva: %d\n",
           SISALTAVA(&t.linkki, Tehtava, linkki)->tunniste);
    printf("fnv1a(\"avain\") = %08x\n", fnv1a("avain"));
    return EXIT_SUCCESS;
}
