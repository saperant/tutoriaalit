// Joukon käyttö rajapinnan kautta: käyttäjä ei tiedä eikä tarvitse
// tietää, että joukko on lajiteltu taulukko.
#include <stdio.h>
#include <stdlib.h>

#include "joukko.h"

// @alku kaytto
static void tulosta(int alkio, void *tieto)
{
    int *monesko = tieto;
    printf("%s%d", (*monesko)++ ? " " : "", alkio);
}

int main(void)
{
    Joukko *luvatut = joukko_luo();
    if (luvatut == nullptr) {
        return EXIT_FAILURE;
    }
    const int portit[] = {443, 22, 80, 443, 8080, 22};
    for (size_t i = 0; i < sizeof portit / sizeof portit[0]; i++) {
        JoukkoTila t = joukko_lisaa(luvatut, portit[i]);
        if (t == JOUKKO_MUISTI) {
            joukko_tuhoa(luvatut);
            return EXIT_FAILURE;
        }
        printf("lisää %4d: %s\n", portit[i],
               t == JOUKKO_ON_JO ? "oli jo" : "lisätty");
    }
    printf("poista 8080: %s\n", joukko_poista(luvatut, 8080)
           == JOUKKO_OK ? "poistettu" : "ei ollut");
    printf("23 sallittu: %s\n",
           joukko_sisaltaa(luvatut, 23) ? "kyllä" : "ei");

    int monesko = 0;
    printf("sallitut (%zu): ", joukko_koko(luvatut));
    joukko_kay_lapi(luvatut, tulosta, &monesko);
    printf("\n");
    joukko_tuhoa(luvatut);
    return EXIT_SUCCESS;
}
// @loppu kaytto
