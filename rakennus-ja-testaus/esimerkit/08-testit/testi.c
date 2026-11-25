#include "testi.h"

int testi_virheet;

int aja_testit(const testi *testit, int maara)
{
    int hylatyt = 0;
    for (int i = 0; i < maara; i++) {
        int ennen = testi_virheet;
        testit[i].funktio();
        int ok = testi_virheet == ennen;
        hylatyt += !ok;
        printf("%s %s\n", ok ? "OK   " : "HYLÄT", testit[i].nimi);
    }
    printf("%d/%d testiä läpi\n", maara - hylatyt, maara);
    return hylatyt ? 1 : 0;
}
