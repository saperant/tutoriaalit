#include <stdio.h>
#include <stdlib.h>

// @alku tyyppi
typedef struct {
    int *data;
    size_t koko;       // alkioita käytössä
    size_t kapasiteetti;   // alkioita varattu
} Vektori;
// @loppu tyyppi

// @alku lisaa
// Lisää alkion loppuun. Palauttaa false, jos muisti loppuu; vektori
// säilyy tällöin ennallaan.
bool vektori_lisaa(Vektori *v, int arvo)
{
    if (v->koko == v->kapasiteetti) {
        size_t uusi = v->kapasiteetti == 0 ? 4 : v->kapasiteetti * 2;
        int *uusi_data = realloc(v->data, uusi * sizeof *uusi_data);
        if (uusi_data == nullptr) {
            return false;   // v->data on yhä voimassa
        }
        v->data = uusi_data;
        v->kapasiteetti = uusi;
        printf("  kapasiteetti -> %zu\n", uusi);
    }
    v->data[v->koko++] = arvo;
    return true;
}

void vektori_vapauta(Vektori *v)
{
    free(v->data);
    *v = (Vektori){};   // nollataan kaikki kentät
}
// @loppu lisaa

int main(void)
{
    // @alku kaytto
    Vektori v = {};
    for (int i = 1; i <= 10; ++i) {
        if (!vektori_lisaa(&v, i * 10)) {
            vektori_vapauta(&v);
            return EXIT_FAILURE;
        }
    }
    printf("koko %zu, viimeinen %d\n", v.koko, v.data[v.koko - 1]);
    vektori_vapauta(&v);
    // @loppu kaytto
}
