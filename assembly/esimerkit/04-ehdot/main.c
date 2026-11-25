// Silmukka ja ehdot: merkkijonon pituus ja arvon rajaus.
#include <stddef.h>
#include <stdio.h>

size_t pituus(const char *s);
long rajaa(long x, long ala, long yla);

int main(void) {
    const char *sanat[] = {"", "a", "konekieli", "Hei, maailma!"};
    for (int i = 0; i < 4; i++) {
        printf("pituus(\"%s\") = %zu\n", sanat[i], pituus(sanat[i]));
    }
    const long arvot[] = {-20, 0, 55, 100, 140};
    for (int i = 0; i < 5; i++) {
        printf("rajaa(%ld, 0, 100) = %ld\n", arvot[i],
               rajaa(arvot[i], 0, 100));
    }
    return 0;
}
