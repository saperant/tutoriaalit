#include <stdio.h>

// @alku vakiot
#define MAKSIMI_VANHA 100          // esikääntäjän makro: pelkkä teksti
constexpr int MAKSIMI = 100;      // C23: tyypitetty vakio
constexpr double PII = 3.14159265358979;
// @loppu vakiot

int main(void)
{
    // @alku bool
    bool valmis = false;           // C23: bool, true ja false ovat
    int taulukko[MAKSIMI] = {};    // avainsanoja; {} nollaa kaiken
    valmis = !valmis;
    // @loppu bool

    // @alku paattely
    auto ala = PII * 2.0 * 2.0;    // C23: tyyppi päätellään (double)
    typeof(ala) kopio = ala;       // C23: lausekkeen tyyppi
    // @loppu paattely

    // @alku const
    const int raja = 10;           // ajoaikainen vakio: ei saa muuttaa
    // @loppu const

    printf("%d %d %d %d\n", MAKSIMI_VANHA, MAKSIMI, valmis, taulukko[99]);
    printf("%.4f %.4f %d\n", ala, kopio, raja);
}
