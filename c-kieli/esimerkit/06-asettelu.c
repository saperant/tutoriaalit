#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

// @alku asettelu
struct huono {
    uint8_t a;    // 1 tavu + 7 tavua täytettä
    uint64_t b;   // 8 tavua
    uint8_t c;    // 1 tavu + 7 tavua täytettä
};

struct hyva {
    uint64_t b;   // 8 tavua
    uint8_t a;    // 1 tavu
    uint8_t c;    // 1 tavu + 6 tavua täytettä
};
// @loppu asettelu

// @alku kartta
typedef struct {
    char merkki;       // kentän tunnus kartassa
    size_t siirtyma;   // kentän etäisyys rakenteen alusta
    size_t koko;
} Kentta;

// Tulostaa rakenteen tavu tavulta: kentän tunnus tai '.', jos tavu on
// täytettä.
void tulosta_kartta(const char *nimi, size_t koko, const Kentta *k,
                    size_t n)
{
    printf("%-13s", nimi);
    for (size_t tavu = 0; tavu < koko; ++tavu) {
        char merkki = '.';
        for (size_t i = 0; i < n; ++i) {
            if (tavu >= k[i].siirtyma && tavu < k[i].siirtyma + k[i].koko) {
                merkki = k[i].merkki;
            }
        }
        putchar(merkki);
    }
    printf("\n");
}
// @loppu kartta

int main(void)
{
    // @alku kaytto
    printf("huono: %zu tavua, b:n siirtymä %zu\n",
           sizeof(struct huono), offsetof(struct huono, b));
    printf("hyvä:  %zu tavua, c:n siirtymä %zu\n",
           sizeof(struct hyva), offsetof(struct hyva, c));

    const Kentta huono[] = {
        {'a', offsetof(struct huono, a), sizeof(uint8_t)},
        {'b', offsetof(struct huono, b), sizeof(uint64_t)},
        {'c', offsetof(struct huono, c), sizeof(uint8_t)},
    };
    const Kentta hyva[] = {
        {'b', offsetof(struct hyva, b), sizeof(uint64_t)},
        {'a', offsetof(struct hyva, a), sizeof(uint8_t)},
        {'c', offsetof(struct hyva, c), sizeof(uint8_t)},
    };
    tulosta_kartta("struct huono", sizeof(struct huono), huono, 3);
    tulosta_kartta("struct hyva", sizeof(struct hyva), hyva, 3);
    // @loppu kaytto
}
