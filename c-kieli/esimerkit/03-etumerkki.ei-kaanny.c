#include <stdio.h>

int main(void)
{
    int pieni = -1;
    unsigned int suuri = 1;
#ifndef KORJATTU
    // -1 muunnetaan etumerkittömäksi: siitä tulee UINT_MAX.
    if (pieni < suuri) {
        printf("-1 < 1\n");
    }
#else
    if (pieni < (int)suuri) {
        printf("-1 < 1\n");
    }
#endif
}
