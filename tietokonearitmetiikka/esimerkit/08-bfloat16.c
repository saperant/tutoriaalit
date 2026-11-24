// float32 -> bfloat16: ylimmät 16 bittiä, pyöristys lähimpään parilliseen.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t bitit(float x)
{
    uint32_t b;
    memcpy(&b, &x, sizeof b);
    return b;
}

static float liukuluvuksi(uint32_t b)
{
    float x;
    memcpy(&x, &b, sizeof x);
    return x;
}

// @alku bf16
static uint16_t bf16(float x)
{
    uint32_t b = bitit(x);
    if ((b & 0x7fffffffu) > 0x7f800000u) {
        return (uint16_t)((b >> 16) | 0x40u);   // NaN pysyy NaN:na
    }
    // Lisätään puolikas ja pariteettibitti: pyöristys lähimpään,
    // tasapelissä parilliseen.
    uint32_t pyoristys = 0x7fffu + ((b >> 16) & 1u);
    return (uint16_t)((b + pyoristys) >> 16);
}

static float bf16_floatiksi(uint16_t h)
{
    return liukuluvuksi((uint32_t)h << 16);    // alaosa nollia
}
// @loppu bf16

int main(void)
{
    const float arvot[] = {1.0f, 3.14159265f, 0.1f, 65504.0f, 1e-38f,
                           3.0e38f, 1.00390625f};
    for (int i = 0; i < 7; i++) {
        uint16_t h = bf16(arvot[i]);
        printf("%-14.9g 0x%08x -> 0x%04x -> %.9g\n", (double)arvot[i],
               bitit(arvot[i]), h, (double)bf16_floatiksi(h));
    }
    return 0;
}
