// Tavallinen virhe: vertailufunktio palauttaa erotuksen a - b. Se
// toimii pienillä luvuilla, mutta INT_MIN - 1 ylivuotaa, ja
// etumerkillisen kokonaisluvun ylivuoto on C:ssä määrittelemätöntä.
// UBSan pysäyttää ohjelman; ilman sitä qsort saisi väärän merkin.
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

// @alku vaarin
static int vertaa_vaarin(const void *x, const void *y)
{
    int a = *(const int *)x, b = *(const int *)y;
    return a - b;                      // ylivuoto, jos a ja b kaukana
}
// @loppu vaarin

int main(void)
{
    int a[] = { 3, INT_MIN, 1, INT_MAX, -2 };
    qsort(a, 5, sizeof a[0], vertaa_vaarin);
    for (int i = 0; i < 5; i++) {
        printf("%d\n", a[i]);
    }
    return EXIT_SUCCESS;
}
