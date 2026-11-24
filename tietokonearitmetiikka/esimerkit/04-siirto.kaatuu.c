// Maskin muodostaminen kentän leveydestä: leveys 32 on liian suuri.
#include <stdint.h>
#include <stdio.h>

static uint32_t maski(unsigned leveys)
{
    // @alku maski
    return (1u << leveys) - 1u;    // leveys 32: määrittelemätön
    // @loppu maski
}

int main(void)
{
    for (unsigned leveys = 30; leveys <= 32; leveys++) {
        printf("%u: 0x%08x\n", leveys, maski(leveys));
    }
    return 0;
}
