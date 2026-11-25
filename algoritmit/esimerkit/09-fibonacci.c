// Päällekkäiset osatehtävät: Fibonaccin luvut kolmella tavalla.
// Suora rekursio laskee samoja arvoja yhä uudelleen (eksponentiaalinen
// määrä kutsuja), muistiinpano laskee kunkin arvon kerran, ja taulukointi
// täyttää taulukon alhaalta ylös ilman rekursiota.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long kutsuja;

// @alku suora
static uint64_t fib_suora(int n)
{
    kutsuja++;
    return n < 2 ? (uint64_t)n : fib_suora(n - 1) + fib_suora(n - 2);
}
// @loppu suora

// @alku muisti
static uint64_t muisti[94];
static bool laskettu[94];

static uint64_t fib_muisti(int n)          // ylhäältä alas
{
    kutsuja++;
    if (n < 2) {
        return (uint64_t)n;
    }
    if (!laskettu[n]) {
        muisti[n] = fib_muisti(n - 1) + fib_muisti(n - 2);
        laskettu[n] = true;
    }
    return muisti[n];
}

static uint64_t fib_taulukko(int n)        // alhaalta ylös
{
    uint64_t edellinen = 0, nykyinen = 1;  // F(0), F(1)
    if (n == 0) {
        return 0;
    }
    for (int i = 2; i <= n; i++) {
        uint64_t seuraava = edellinen + nykyinen;
        edellinen = nykyinen;
        nykyinen = seuraava;
    }
    return nykyinen;
}
// @loppu muisti

// Kutsupuut sulkulausekkeina (argumentti ja lasten puut): suora
// rekursio ja muistiinpano, jossa tähti merkitsee muistista saatua
// arvoa. Kirjan kuva piirretään näistä riveistä (kaaviot/tee.py).
static void puu_suora(int n)
{
    printf("(%d", n);
    if (n >= 2) {
        printf(" ");
        puu_suora(n - 1);
        printf(" ");
        puu_suora(n - 2);
    }
    printf(")");
}

static void puu_muisti(int n)
{
    if (n < 2 || laskettu[n]) {
        printf("(%d%s)", n, n < 2 ? "" : "*");
        return;
    }
    printf("(%d ", n);
    puu_muisti(n - 1);
    printf(" ");
    puu_muisti(n - 2);
    printf(")");
    laskettu[n] = true;
}

int main(void)
{
    printf("kutsupuu F(5), suora:  ");
    puu_suora(5);
    printf("\nkutsupuu F(5), muisti: ");
    puu_muisti(5);
    printf("\n");
    printf("%3s %22s %12s %10s\n", "n", "F(n)", "suora", "muisti");
    for (int n = 10; n <= 30; n += 5) {
        kutsuja = 0;
        uint64_t a = fib_suora(n);
        long suora = kutsuja;
        kutsuja = 0;
        memset(laskettu, 0, sizeof laskettu);   // tyhjä muisti
        uint64_t b = fib_muisti(n);
        printf("%3d %22llu %12ld %10ld%s\n", n, (unsigned long long)a,
               suora, kutsuja, a == b && b == fib_taulukko(n) ? "" : " !");
    }
    // F(93) on suurin, joka mahtuu 64-bittiseen etumerkittömään lukuun.
    printf("%3d %22llu %12s %10s\n", 93,
           (unsigned long long)fib_taulukko(93), "-", "-");
    return EXIT_SUCCESS;
}
