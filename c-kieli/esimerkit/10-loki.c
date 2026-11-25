#include <stdarg.h>
#include <stdio.h>

// @alku loki
typedef enum { TIETO, VAROITUS, VIRHE } Taso;

// Attribuutti kertoo kääntäjälle, että parametri 2 on printf-tyylinen
// muotoilumerkkijono ja sen argumentit alkavat parametrista 3.
[[gnu::format(printf, 2, 3)]]
void loki(Taso taso, const char *muoto, ...)
{
    static const char *const NIMET[] = {"tieto", "varoitus", "virhe"};
    va_list argumentit;
    va_start(argumentit, muoto);
    printf("[%s] ", NIMET[taso]);
    vprintf(muoto, argumentit);   // v-versio ottaa va_list-argumentin
    putchar('\n');
    va_end(argumentit);
}
// @loppu loki

int main(void)
{
    // @alku kaytto
    loki(TIETO, "palvelin kuuntelee porttia %d", 8080);
    loki(VAROITUS, "levytilaa jäljellä %.1f %%", 4.5);
    loki(VIRHE, "tiedostoa %s ei löydy", "asetukset.ini");
    // @loppu kaytto
}
