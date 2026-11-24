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
