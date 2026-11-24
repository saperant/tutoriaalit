// Rajasykli: kiinteapilkkuinen IIR ei vaimene nollaan ilman syotetta.
#include <stdint.h>
#include <stdio.h>

// @alku suodin
// y[n] = a * y[n-1], a = 0,9 Q1.15-muodossa. Syote on nolla.
static const int32_t A = 29491;                 // round(0.9 * 32768)

static int16_t pyorista(int32_t tulo)           // Q2.30 -> Q1.15
{
    return (int16_t)((tulo + (1 << 14)) >> 15);  // lahimpaan
}

static int16_t katkaise(int32_t tulo)           // kohti nollaa
{
    return (int16_t)(tulo >= 0 ? tulo >> 15 : -(-tulo >> 15));
}
// @loppu suodin

// @alku ajo
static void aja(const char *nimi, int16_t (*kvantisoi)(int32_t),
                int32_t a)
{
    int16_t y = 1000;
    printf("%-10s a = %+.3f:", nimi, a / 32768.0);
    for (int n = 1; n <= 60; n++) {
        y = kvantisoi(a * y);
        if (n % 20 == 0 || n >= 57) {     // muutama nayte ja loppu
            printf(" %4d", y);
        }
    }
    printf("\n");
}

int main(void)
{
    aja("pyoristys", pyorista, A);
    aja("pyoristys", pyorista, -A);
    aja("katkaisu", katkaise, A);
    aja("katkaisu", katkaise, -A);
    return 0;
}
// @loppu ajo
