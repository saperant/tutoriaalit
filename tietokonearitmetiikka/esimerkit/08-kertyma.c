// int8-pistetulo: tulot mahtuvat 16 bittiin, mutta niiden summa ei.
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    enum { N = 64 };
    int8_t paino[N], syote[N];
    for (int i = 0; i < N; i++) {
        paino[i] = 127;               // pahin tapaus: kaikki ääriarvoja
        syote[i] = (int8_t)(i % 2 ? 127 : 100);
    }
    // @alku kertyma
    int16_t kapea = 0;
    int32_t levea = 0;
    for (int i = 0; i < N; i++) {
        int16_t tulo = (int16_t)(paino[i] * syote[i]);   // <= 16129
        kapea = (int16_t)(kapea + tulo);   // muunnos kiertää hiljaa
        levea += tulo;
    }
    // @loppu kertyma
    printf("int16-kertymä %d, int32-kertymä %d\n", kapea, levea);
    return 0;
}
