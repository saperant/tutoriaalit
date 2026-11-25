// Globaali data: laskuri (.data), kutsujen määrä (.bss), vakiotaulukko
// (.rodata) ja 64-bittinen vakio.
#include <stdio.h>

long seuraava(void);
long alkuluku(long i);
unsigned long vakio(void);
extern long laskuri;       // assembly-tiedoston symbolit näkyvät C:hen
extern long kutsuja;

int main(void) {
    printf("laskuri aluksi %ld, kutsuja %ld\n", laskuri, kutsuja);
    seuraava();
    printf("seuraava() = %ld\n", seuraava());
    printf("laskuri lopuksi %ld, kutsuja %ld\n", laskuri, kutsuja);
    printf("alkuluvut:");
    for (long i = 0; i < 5; i++) {
        printf(" %ld", alkuluku(i));
    }
    printf("\nvakio = %#lx\n", vakio());
    return 0;
}
