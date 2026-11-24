// Käyttöoikeudet bittilippuina: yksi bitti kutakin oikeutta kohden.
#include <stdint.h>
#include <stdio.h>

// @alku liput
enum : uint8_t {
    LUKU = 1u << 0,
    KIRJOITUS = 1u << 1,
    POISTO = 1u << 2,
    HALLINTA = 1u << 3,
};
// @loppu liput

static void tulosta(const char *kuka, uint8_t oikeudet)
{
    printf("%-9s 0x%02x %c%c%c%c\n", kuka, oikeudet,
           oikeudet & LUKU ? 'L' : '-', oikeudet & KIRJOITUS ? 'K' : '-',
           oikeudet & POISTO ? 'P' : '-', oikeudet & HALLINTA ? 'H' : '-');
}

int main(void)
{
    // @alku operaatiot
    uint8_t vieras = LUKU;
    uint8_t toimittaja = LUKU | KIRJOITUS;            // aseta
    uint8_t yllapito = LUKU | KIRJOITUS | POISTO | HALLINTA;
    uint8_t rajattu = yllapito & (uint8_t)~HALLINTA;   // poista
    uint8_t vaihdettu = toimittaja ^ POISTO;           // vaihda
    bool saa_kirjoittaa = (rajattu & KIRJOITUS) != 0;  // testaa
    bool kaikki = (yllapito & (LUKU | POISTO)) == (LUKU | POISTO);
    // @loppu operaatiot
    tulosta("vieras", vieras);
    tulosta("toimitt.", toimittaja);
    tulosta("hallinta", yllapito);
    tulosta("rajattu", rajattu);
    tulosta("vaihdettu", vaihdettu);
    printf("%d %d\n", saa_kirjoittaa, kaikki);
    return 0;
}
