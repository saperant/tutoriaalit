// Rakenteen täyte, kenttien järjestys ja väärä jakaminen.
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

// @alku tayte
// Kentät kirjoitusjärjestyksessä: kääntäjä lisää täytettä, jotta
// double on kahdeksalla jaollisessa osoitteessa.
typedef struct {
    char tyyppi;
    double arvo;
    char tila;
    int maara;
} Huono;

// Suurimmat kentät ensin: sama sisältö pienemmässä tilassa.
typedef struct {
    double arvo;
    int maara;
    char tyyppi;
    char tila;
} Hyva;
// @loppu tayte

// @alku jakaminen
// Kaksi laskuria samalla välimuistirivillä: kun kaksi säiettä kirjoittaa
// kumpikin omaansa, rivi pomppii ytimeltä toiselle (väärä jakaminen).
typedef struct {
    long a;
    long b;
} Vierekkain;

// alignas(64) aloittaa kummankin laskurin omalta riviltään.
typedef struct {
    alignas(64) long a;
    alignas(64) long b;
} Erillaan;
// @loppu jakaminen

enum { KIERROKSIA = 50000000 };

static void *kasvata(void *p)
{
    long *laskuri = p;
    for (long i = 0; i < KIERROKSIA; i++) {
        (*laskuri)++;
        kayta(laskuri);     // pakottaa kirjoituksen muistiin joka kerta
    }
    return NULL;
}

typedef struct {
    long *a, *b;
} Laskurit;

static void kaksi_saietta(void *p)
{
    Laskurit *l = p;
    pthread_t s1, s2;
    if (pthread_create(&s1, NULL, kasvata, l->a) != 0
        || pthread_create(&s2, NULL, kasvata, l->b) != 0) {
        perror("pthread_create");
        exit(EXIT_FAILURE);
    }
    pthread_join(s1, NULL);
    pthread_join(s2, NULL);
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        static Vierekkain v;
        static Erillaan e;
        Laskurit samalla = {&v.a, &v.b}, eri = {&e.a, &e.b};
        printf("kaksi saietta, kumpikin kasvattaa omaa laskuriaan\n");
        Tilasto t1 = mittaa(kaksi_saietta, &samalla, 7);
        Tilasto t2 = mittaa(kaksi_saietta, &eri, 7);
        tulosta_mittaus("samalla rivilla", t1, 0);
        tulosta_mittaus("eri riveilla", t2, t1.mediaani);
        return 0;
    }
    // @alku testi
    printf("Huono: koko %2zu, arvo @%zu, tila @%zu, maara @%zu\n",
           sizeof(Huono), offsetof(Huono, arvo), offsetof(Huono, tila),
           offsetof(Huono, maara));
    printf("Hyva:  koko %2zu, arvo @%zu, tila @%zu, maara @%zu\n",
           sizeof(Hyva), offsetof(Hyva, arvo), offsetof(Hyva, tila),
           offsetof(Hyva, maara));
    printf("Vierekkain: koko %3zu, b @%zu\n", sizeof(Vierekkain),
           offsetof(Vierekkain, b));
    printf("Erillaan:   koko %3zu, b @%zu\n", sizeof(Erillaan),
           offsetof(Erillaan, b));
    // @loppu testi
    return 0;
}
