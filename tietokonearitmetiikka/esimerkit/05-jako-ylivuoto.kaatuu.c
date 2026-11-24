// Pienimmän int-arvon jakaminen luvulla -1 ylivuotaa.
#include <limits.h>
#include <stdio.h>

static int keskiarvo(int summa, int lukumaara)
{
    return summa / lukumaara;
}

int main(void)
{
    // @alku jako
    printf("%d\n", keskiarvo(INT_MIN, -1));   // tulos 2^31 ei mahdu
    // @loppu jako
    return 0;
}
