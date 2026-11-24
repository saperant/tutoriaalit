// Näyttöohjaimen RGB565-pikseli: 5 bittiä punaista, 6 vihreää, 5 sinistä.
#include <stdint.h>
#include <stdio.h>

// @alku pakkaus
static uint16_t pakkaa(uint8_t r, uint8_t g, uint8_t b)
{
    return (uint16_t)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

static void pura(uint16_t p, uint8_t *r, uint8_t *g, uint8_t *b)
{
    uint8_t r5 = (p >> 11) & 0x1f;
    uint8_t g6 = (p >> 5) & 0x3f;
    uint8_t b5 = p & 0x1f;
    // Ylimmät bitit toistetaan alimpiin: 0x1f -> 0xff eikä 0xf8.
    *r = (uint8_t)((r5 << 3) | (r5 >> 2));
    *g = (uint8_t)((g6 << 2) | (g6 >> 4));
    *b = (uint8_t)((b5 << 3) | (b5 >> 2));
}
// @loppu pakkaus

int main(void)
{
    const uint8_t varit[][3] = {{255, 255, 255}, {255, 128, 0},
                                {18, 52, 86}, {0, 0, 0}};
    for (int i = 0; i < 4; i++) {
        uint16_t p = pakkaa(varit[i][0], varit[i][1], varit[i][2]);
        uint8_t r, g, b;
        pura(p, &r, &g, &b);
        printf("(%3u,%3u,%3u) -> 0x%04x -> (%3u,%3u,%3u)\n", varit[i][0],
               varit[i][1], varit[i][2], p, r, g, b);
    }
    return 0;
}
