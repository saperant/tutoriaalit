// Puolitushaun keskikohta: (ala + yla) / 2 voi ylivuotaa.
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    uint32_t ala = 3000000000u;
    uint32_t yla = 4000000000u;
    // @alku keskikohta
    uint32_t vaara = (ala + yla) / 2;          // summa kiertää
    uint32_t oikea = ala + (yla - ala) / 2;    // ei voi ylivuotaa
    // @loppu keskikohta
    printf("väärin %u, oikein %u\n", vaara, oikea);
    return 0;
}
