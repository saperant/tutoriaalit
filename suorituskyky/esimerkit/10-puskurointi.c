// I/O-puskurointi: montako järjestelmäkutsua kirjoitus maksaa.
#define _GNU_SOURCE             // fopencookie
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "mittari.h"

// @alku laskuri
// Virta, joka kirjoittaa tiedostokuvaajaan ja laskee write-kutsut.
// fopencookie (glibc) antaa stdio-puskuroinnin omalle kirjoitusfunktiolle.
typedef struct {
    int fd;
    size_t kutsuja;
} Kohde;

static ssize_t kirjoita(void *k, const char *data, size_t koko)
{
    Kohde *kohde = k;
    kohde->kutsuja++;
    return write(kohde->fd, data, koko);
}

static FILE *avaa(Kohde *kohde)
{
    return fopencookie(kohde, "w", (cookie_io_functions_t){
        .write = kirjoita});
}
// @loppu laskuri

enum { RIVEJA = 100000 };

// @alku tavat
// 1. Oma write-kutsu jokaiselle riville.
static void rivi_kerrallaan(Kohde *k, int riveja)
{
    char rivi[32];
    for (int i = 0; i < riveja; i++) {
        int n = snprintf(rivi, sizeof rivi, "rivi %d\n", i);
        kirjoita(k, rivi, (size_t)n);
    }
}

// 2. stdio-puskuri, koko annettuna (0 = kirjaston oletus). glibc ei
// noudata setvbuf-funktion kokoa, jos puskuria ei anneta, joten se
// varataan itse. Puskurin on elettävä, kunnes virta on suljettu.
static void puskuroitu(Kohde *k, int riveja, size_t koko)
{
    FILE *f = avaa(k);
    char *puskuri = koko > 0 ? malloc(koko) : NULL;
    if (f == NULL || (koko > 0 && puskuri == NULL)) {
        perror("puskuroitu");
        exit(EXIT_FAILURE);
    }
    if (koko > 0) {
        setvbuf(f, puskuri, _IOFBF, koko);
    }
    for (int i = 0; i < riveja; i++) {
        fprintf(f, "rivi %d\n", i);
    }
    fclose(f);              // tyhjentää puskurin viimeisen kerran
    free(puskuri);
}
// @loppu tavat

static int tilapaistiedosto(void)
{
    FILE *f = tmpfile();
    if (f == NULL) {
        perror("tmpfile");
        exit(EXIT_FAILURE);
    }
    return dup(fileno(f));      // kuvaaja jää auki, kun f suljetaan
}

static void tulosta(const char *nimi, Kohde *k)
{
    off_t koko = lseek(k->fd, 0, SEEK_END);
    printf("  %-22s %7zu write-kutsua, %ld tavua\n", nimi, k->kutsuja,
           (long)koko);
}

typedef struct {
    int tapa;
    size_t kutsuja;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    Kohde k = {tilapaistiedosto(), 0};
    if (t->tapa == 0) {
        rivi_kerrallaan(&k, RIVEJA);
    } else {
        puskuroitu(&k, RIVEJA, t->tapa == 1 ? 0 : 1 << 16);
    }
    t->kutsuja = k.kutsuja;
    close(k.fd);
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        printf("%d rivin kirjoitus tiedostoon\n", RIVEJA);
        const char *nimet[] = {"write / rivi", "stdio, oletuspuskuri",
                               "stdio, 64 KiB puskuri"};
        double vertailu = 0;
        for (int i = 0; i < 3; i++) {
            Tila t = {i, 0};
            Tilasto s = mittaa(aja, &t, 11);
            tulosta_mittaus(nimet[i], s, vertailu);
            vertailu = i == 0 ? s.mediaani : vertailu;
        }
        return 0;
    }
    // --kerran TAPA: yksi kirjoitustapa kerran (strace-tarkistusta varten).
    if (argc > 2 && strcmp(argv[1], "--kerran") == 0) {
        Tila t = {atoi(argv[2]), 0};
        aja(&t);
        return 0;
    }
    // @alku testi
    printf("%d rivia\n", RIVEJA);
    Kohde a = {tilapaistiedosto(), 0};
    rivi_kerrallaan(&a, RIVEJA);
    tulosta("write / rivi", &a);
    Kohde b = {tilapaistiedosto(), 0};
    puskuroitu(&b, RIVEJA, 0);
    tulosta("stdio, oletuspuskuri", &b);
    Kohde c = {tilapaistiedosto(), 0};
    puskuroitu(&c, RIVEJA, 1 << 16);
    tulosta("stdio, 64 KiB puskuri", &c);
    // @loppu testi
    close(a.fd);
    close(b.fd);
    close(c.fd);
    return 0;
}
