#include <stdio.h>

enum suunta { POHJOINEN, ITA, ETELA, LANSI };

const char *nimi(enum suunta s)
{
    switch (s) {
    case POHJOINEN: return "pohjoinen";
    case ITA: return "itä";
    case ETELA: return "etelä";
#ifdef KORJATTU
    case LANSI: return "länsi";
#endif
    }
    return "?";
}

int main(void)
{
    printf("%s\n", nimi(ETELA));
}
