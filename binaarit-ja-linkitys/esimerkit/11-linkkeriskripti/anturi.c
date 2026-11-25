#include <stdint.h>
#include <stdio.h>

// @alku taulu
// Tehtaalla kirjoitettava kalibrointitaulu omaan osioonsa, jotta sen
// voi korvata valmiista ohjelmasta tai tiedostosta tunnetusta kohdasta.
__attribute__((used, section(".kalibrointi")))
static const int16_t korjaus[4] = {-12, 3, 0, 7};

extern const char __kalibrointi_alku[], __kalibrointi_loppu[];
// @loppu taulu

int main(void)
{
    // @alku kaytto
    printf("taulun koko %zu tavua\n",
           (size_t)(__kalibrointi_loppu - __kalibrointi_alku));
    printf("taulu sivun alussa: %s\n",
           (uintptr_t)__kalibrointi_alku % 4096 == 0 ? "kyllä" : "ei");
    // @loppu kaytto
    printf("anturin 0 korjaus: %d\n", korjaus[0]);
    return 0;
}
