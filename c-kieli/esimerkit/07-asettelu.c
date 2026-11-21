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

int main(void)
{
    // @alku kaytto
    printf("huono: %zu tavua, b:n siirtymä %zu\n",
           sizeof(struct huono), offsetof(struct huono, b));
    printf("hyvä:  %zu tavua, c:n siirtymä %zu\n",
           sizeof(struct hyva), offsetof(struct hyva, c));
    // @loppu kaytto
}
