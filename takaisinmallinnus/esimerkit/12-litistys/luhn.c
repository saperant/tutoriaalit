// Luhnin tarkistus kahdesti: tavallisena ja ohjausvuoltaan
// litistettynä sekä läpinäkymättömällä predikaatilla höystettynä.
#include <stdio.h>
#include <string.h>

// @alku tavallinen
int luhn(const char *numero)
{
    int summa = 0;
    int tuplaa = 0;
    for (int i = (int)strlen(numero) - 1; i >= 0; i--) {
        int d = numero[i] - '0';
        if (tuplaa) {
            d *= 2;
            if (d > 9) {
                d -= 9;
            }
        }
        summa += d;
        tuplaa = !tuplaa;
    }
    return summa % 10 == 0;
}
// @loppu tavallinen

// @alku litistetty
// Sama funktio litistettynä: jokainen peruslohko on switch-haara, ja
// seuraava lohko valitaan tilamuuttujalla. Tilojen arvot ovat
// satunnaisia, jotta järjestys ei paljastu.
int luhn_litistetty(const char *numero)
{
    int summa = 0, tuplaa = 0, i = 0, d = 0;
    unsigned tila = 0x6b2f9c01u;
    for (;;) {
        switch (tila) {
        case 0x6b2f9c01u:
            i = (int)strlen(numero) - 1;
            tila = 0x1d44e7a3u;
            break;
        case 0x1d44e7a3u:
            tila = i >= 0 ? 0x93c0558eu : 0x0c71b2d4u;
            break;
        case 0x93c0558eu:
            d = numero[i] - '0';
            // Läpinäkymätön predikaatti: i * (i + 1) on aina parillinen.
            tila = (unsigned)(i * (i + 1)) % 2u == 0 ? 0x47a8d316u
                                                     : 0xe5013b7cu;
            break;
        case 0xe5013b7cu: // kuollut haara: ei suoriteta koskaan
            summa ^= 0x55;
            tila = 0x0c71b2d4u;
            break;
        case 0x47a8d316u:
            tila = tuplaa ? 0xb85e20f9u : 0x2a9364c5u;
            break;
        case 0xb85e20f9u:
            d = d * 2 > 9 ? d * 2 - 9 : d * 2;
            tila = 0x2a9364c5u;
            break;
        case 0x2a9364c5u:
            summa += d;
            tuplaa = !tuplaa;
            i--;
            tila = 0x1d44e7a3u;
            break;
        case 0x0c71b2d4u:
            return summa % 10 == 0;
        }
    }
}
// @loppu litistetty

int main(void)
{
    const char *numerot[] = {"79927398713", "79927398710", "4539578763621486",
                             "1234567812345678", "0"};
    for (size_t k = 0; k < sizeof numerot / sizeof numerot[0]; k++) {
        printf("%-17s %d %d\n", numerot[k], luhn(numerot[k]),
               luhn_litistetty(numerot[k]));
    }
    return 0;
}
