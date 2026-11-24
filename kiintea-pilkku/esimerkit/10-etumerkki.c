// 12-bittisen AD-muuntimen näyte 16-bittisestä rekisteristä.
#include <stdint.h>
#include <stdio.h>

// @alku laajennus
// Rekisterin alimmat 12 bittiä ovat etumerkillinen näyte (kahden
// komplementti), ylimmät neljä bittiä ovat tilabittejä.
static int32_t vaarin(uint16_t rekisteri)
{
    return rekisteri & 0x0fff;              // etumerkki katoaa
}

static int32_t oikein(uint16_t rekisteri)
{
    int32_t x = rekisteri & 0x0fff;
    return (x ^ 0x800) - 0x800;             // bitti 11 etumerkiksi
}
// @loppu laajennus

int main(void)
{
    // @alku koe
    const uint16_t rekisterit[] = {0x07ff, 0xa001, 0x5fff, 0x3800};
    for (size_t i = 0; i < 4; i++) {
        printf("0x%04x: väärin %5d, oikein %5d\n", rekisterit[i],
               vaarin(rekisterit[i]), oikein(rekisterit[i]));
    }
    // @loppu koe
    return 0;
}
