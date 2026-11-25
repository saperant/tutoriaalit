#include <stdio.h>

// @alku muuttujat
const int kuukausien_paivat[12] = {31, 28, 31, 30, 31, 30,
                                   31, 31, 30, 31, 30, 31};
int laskuri = 5;            // alustettu globaali
int puskuri[4096];          // nollalla alustettu globaali
static int kutsuja;         // nollalla alustettu, vain tässä tiedostossa

int paivia_vuodessa(void)
{
    static int valimuisti = -1;   // alustettu, vain tässä funktiossa
    ++kutsuja;
    if (valimuisti < 0) {
        valimuisti = 0;
        for (int i = 0; i < 12; ++i)
            valimuisti += kuukausien_paivat[i];
    }
    return valimuisti;
}
// @loppu muuttujat

int main(void)
{
    puskuri[0] = laskuri;
    printf("%s %d\n", "päiviä vuodessa:", paivia_vuodessa());
    return puskuri[4095];
}
