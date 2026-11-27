// Kide-ohjelmien ajonaikainen kirjasto. Käännetään RISC-V:lle ja
// linkitetään kääntäjän tuottaman assemblyn kanssa.
#include <stdio.h>

// @alku kirjasto
long k_main(void);              // Kide-ohjelman main

void kide_tulosta(long arvo) {  // print(arvo)
    printf("%ld\n", arvo);
}

int main(void) {
    return (int)k_main();
}
// @loppu kirjasto

// Valinnalla --laske käännetty koodi kasvattaa tätä laskuria, ja summa
// tulostetaan ohjelman lopuksi virhevirtaan.
long kide_kaskyja;

__attribute__((destructor)) static void tulosta_kaskyt(void) {
    if (kide_kaskyja > 0) fprintf(stderr, "käskyjä %ld\n", kide_kaskyja);
}
