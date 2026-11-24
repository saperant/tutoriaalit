// Kertymä int32_t:ssä: etumerkillinen ylivuoto on määrittelemätön.
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    // @alku kertyma
    const int16_t x[4] = {-32768, -32768, -32768, -32768};   // -1,0
    int32_t kertyma = 0;
    for (int i = 0; i < 4; i++) {
        kertyma += (int32_t)x[i] * x[i];    // 2^30 kertaa neljä
    }
    // @loppu kertyma
    printf("%d\n", kertyma);
    return 0;
}
