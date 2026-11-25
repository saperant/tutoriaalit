// Osoitusmuodot: taulukon alkio ja tietueen kentät.
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

// @alku tuote
struct tuote {
    int32_t koodi;
    int32_t maara;
    int64_t hinta_snt;
};
_Static_assert(offsetof(struct tuote, maara) == 4, "asettelu");
_Static_assert(offsetof(struct tuote, hinta_snt) == 8, "asettelu");
_Static_assert(sizeof(struct tuote) == 16, "asettelu");
// @loppu tuote

int32_t hae(const int32_t *t, long i);
int64_t varaston_arvo(const struct tuote *t, long n);

int main(void) {
    const int32_t lampotilat[] = {-3, 1, 7, 12, 4};
    printf("hae(t, 2) = %d\n", hae(lampotilat, 2));
    const struct tuote varasto[] = {
        {101, 12, 249}, {102, 3, 1590}, {103, 40, 95},
    };
    long n = sizeof varasto / sizeof varasto[0];
    printf("varaston arvo: %lld snt\n",
           (long long)varaston_arvo(varasto, n));
    printf("tyhjä varasto: %lld snt\n",
           (long long)varaston_arvo(varasto, 0));
    return 0;
}
