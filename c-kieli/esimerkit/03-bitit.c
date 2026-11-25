#include <stdbit.h>
#include <stdint.h>
#include <stdio.h>

// @alku kentat
// Ohjausrekisterin kentät:
//   bitit 15..8  näytetaajuus
//   bitti 7      mittaus päällä
//   bitit 6..4   vahvistus
//   bitit 3..0   kanava
constexpr uint16_t KANAVA_MASKI = 0x0F;
constexpr unsigned VAHVISTUS_SIIRTO = 4;
constexpr uint16_t VAHVISTUS_MASKI = 0x07;
constexpr uint16_t PAALLA = 1u << 7;
constexpr unsigned TAAJUUS_SIIRTO = 8;

uint16_t pakkaa(unsigned kanava, unsigned vahvistus, unsigned taajuus)
{
    return (uint16_t)((taajuus << TAAJUUS_SIIRTO)
                      | ((vahvistus & VAHVISTUS_MASKI) << VAHVISTUS_SIIRTO)
                      | (kanava & KANAVA_MASKI));
}

// Kentän poiminta: siirretään kenttä alimpiin bitteihin ja maskataan.
unsigned vahvistus(uint16_t rekisteri)
{
    return (rekisteri >> VAHVISTUS_SIIRTO) & VAHVISTUS_MASKI;
}
// @loppu kentat

// Tulostaa tavun bitit eniten merkitsevästä alkaen.
static void bitit(const char *nimi, uint8_t x)
{
    printf("%-6s = ", nimi);
    for (int i = 7; i >= 0; --i) {
        putchar(((x >> i) & 1) != 0 ? '1' : '0');
    }
    putchar('\n');
}

int main(void)
{
    // @alku perus
    uint8_t a = 0b1100'1010;
    uint8_t b = 0b0000'1111;
    bitit("a", a);
    bitit("b", b);
    bitit("a & b", a & b);              // JA: 1, jos molemmissa 1
    bitit("a | b", a | b);              // TAI: 1, jos jommassakummassa 1
    bitit("a ^ b", a ^ b);              // poissulkeva TAI: 1, jos eri
    bitit("~a", (uint8_t)~a);           // kääntää jokaisen bitin
    bitit("a << 2", (uint8_t)(a << 2)); // siirto vasemmalle
    bitit("a >> 2", a >> 2);            // siirto oikealle
    // @loppu perus

    // @alku rekisteri
    uint16_t r = pakkaa(5, 3, 100);
    printf("pakattu:   0x%04x\n", r);

    r |= PAALLA;                 // asettaa bitin
    printf("asetettu:  0x%04x\n", r);
    r &= (uint16_t)~PAALLA;      // nollaa bitin
    printf("nollattu:  0x%04x\n", r);
    r ^= PAALLA;                 // vaihtaa bitin tilan
    if ((r & PAALLA) != 0) {     // testaa bitin
        printf("mittaus on päällä\n");
    }

    printf("kanava %u, vahvistus %u, taajuus %u\n",
           r & KANAVA_MASKI, vahvistus(r), r >> TAAJUUS_SIIRTO);
    printf("ykkösbittejä: %u\n", stdc_count_ones(r));
    // @loppu rekisteri
}
