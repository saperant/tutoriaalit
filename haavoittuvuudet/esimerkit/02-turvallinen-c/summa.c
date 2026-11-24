/* Viestin kokonaispituus: otsake + data. Etumerkillinen ylivuoto on
 * C:ssä määrittelemätöntä käytöstä, jonka UBSan havaitsee. */
#include <limits.h>
#include <stdckdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { OTSAKE = 16 };

// @alku summa
static int kokonaispituus(int data)
{
#ifdef KORJATTU
    int tulos;
    if (ckd_add(&tulos, data, OTSAKE)) {
        return -1;
    }
    return tulos;
#else
    return data + OTSAKE;               /* VIRHE: voi ylivuotaa */
#endif
}
// @loppu summa

int main(int argc, char *argv[])
{
    int data = argc > 1 ? (int)strtol(argv[1], NULL, 10) : 0;
    printf("kokonaispituus: %d\n", kokonaispituus(data));
    return 0;
}
