// C:n jakolasku katkaisee kohti nollaa. Kellonajan laskenta tarvitsee
// lattiajaon, joka pyöristää kohti miinus ääretöntä.
#include <stdio.h>

// @alku lattia
static int lattiajako(int a, int b)
{
    int q = a / b;
    return (a % b != 0 && (a < 0) != (b < 0)) ? q - 1 : q;
}

static int lattiajaannos(int a, int b)
{
    int r = a % b;
    return (r != 0 && (r < 0) != (b < 0)) ? r + b : r;
}
// @loppu lattia

int main(void)
{
    // @alku c
    printf(" 7 / 2 = %d,  7 %% 2 = %d\n", 7 / 2, 7 % 2);
    printf("-7 / 2 = %d, -7 %% 2 = %d\n", -7 / 2, -7 % 2);
    printf(" 7 / -2 = %d,  7 %% -2 = %d\n", 7 / -2, 7 % -2);
    // @loppu c
    // Kello 00.15 miinus 45 minuuttia vuorokauden minuuteissa.
    int minuutit = 15 - 45;
    int kello = lattiajaannos(minuutit, 24 * 60);
    printf("%%: %d, lattia: %02d.%02d (päivä %+d)\n", minuutit % 1440,
           kello / 60, kello % 60, lattiajako(minuutit, 1440));
    // @alku katto
    int riveja = 101, sivulle = 25;
    int sivuja = (riveja + sivulle - 1) / sivulle;   // kattojako
    // @loppu katto
    printf("%d sivua\n", sivuja);
    return 0;
}
