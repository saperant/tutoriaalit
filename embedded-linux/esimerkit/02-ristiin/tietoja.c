// Kertoo, millaiselle alustalle ohjelma on käännetty ja millä se ajetaan.
// Sama lähdekoodi käännetään isännälle ja ARM64:lle: erot näkyvät
// tulosteessa, vaikka koodissa ei ole yhtään alustakohtaista riviä.

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/utsname.h>

int main(void)
{
    struct utsname u;
    if (uname(&u) != 0) {
        perror("uname");
        return 1;
    }
    // @alku erot
    const uint16_t tavut = 0x0102;
    const int pieni = *(const unsigned char *)&tavut == 0x02;
    printf("suoritin:      %s\n", u.machine);
    printf("long:          %zu tavua\n", sizeof(long));
    printf("osoitin:       %zu tavua\n", sizeof(void *));
    printf("tavujarjestys: %s\n", pieni ? "little-endian" : "big-endian");
    // C-standardi jättää char-tyypin etumerkin toteutuksen päätettäväksi.
    printf("char:          %s\n", CHAR_MIN < 0 ? "etumerkillinen"
                                               : "etumerkiton");
    // @loppu erot
    return 0;
}
