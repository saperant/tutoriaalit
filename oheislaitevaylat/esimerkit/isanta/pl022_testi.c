/* PL022-ajurin testi isäntäkoneella. Rekisterien paikalla on
 * tavallinen muistisivu: kun SR:ään asetetaan TNF ja RNE, DR:n kautta
 * kirjoitettu tavu luetaan samasta muistipaikasta takaisin. Sivu
 * käyttäytyy siis kuin silmukkatilassa oleva lohko, mutta vain yhden
 * kehyksen siirroissa: muistipaikka ei ole FIFO. */
#include <stdio.h>
#include <string.h>

#include "pl022.h"

// @alku sivu
static uint32_t sivu[0x400];         /* 4 KiB:n rekisteri-ikkuna */
static pl022_t *const spi = (pl022_t *)sivu;
enum { SR = 3 };                     /* SR:n sanaindeksi (0x0C) */
// @loppu sivu

static int virheita;

static void tarkista(const char *nimi, int ehto) {
    printf("%-40s %s\n", nimi, ehto ? "ok" : "VIRHE");
    virheita += !ehto;
}

// @alku testit
int main(void) {
    static const struct {
        uint32_t haluttu;
        uint32_t odotettu;
    } kellot[] = {
        {12500000u, 12500000u}, {10000000u, 6250000u},
        {1000000u, 961538u},    {400000u, 390625u},
        {1000u, 1000u},
        {300u, 0u}, /* liian hidas: 25 MHz / (254 * 256) = 384 Hz */
    };
    for (size_t i = 0; i < sizeof kellot / sizeof kellot[0]; i++) {
        pl022_kello_t k = {0, 0, 0};
        spi_tila_t t = pl022_kello(25000000u, kellot[i].haluttu, &k);
        uint32_t saatu = t == SPI_OK ? k.taajuus : 0;
        printf("SCK %8u Hz -> %8u Hz (CPSDVSR %3u, SCR %3u)\n",
               (unsigned)kellot[i].haluttu, (unsigned)saatu, k.cpsdvsr,
               k.scr);
        virheita += saatu != kellot[i].odotettu;
    }

    tarkista("alustus: moodi 3, 8 bittia",
             pl022_alusta(spi, 25000000u, 1000000u, 3, 8) == SPI_OK &&
                 spi->CR0 == 0x0CC7u && spi->CPSR == 2u &&
                 spi->CR1 == PL022_CR1_SSE);
    tarkista("alustus: moodi 4 hylataan",
             pl022_alusta(spi, 25000000u, 1000000u, 4, 8) ==
                 SPI_PARAMETRI);

    sivu[SR] = PL022_SR_TNF | PL022_SR_RNE;
    const uint8_t tx[20] = "silmukka toimii ok!";
    uint8_t rx[20] = {0};
    int ok = 1;
    for (size_t i = 0; i < sizeof tx; i++) {
        ok &= pl022_siirto(spi, &tx[i], &rx[i], 1) == SPI_OK;
    }
    tarkista("20 yhden tavun siirtoa muistisivun kautta",
             ok && memcmp(tx, rx, sizeof tx) == 0);

    sivu[SR] = PL022_SR_BSY; /* FIFO täynnä eikä mitään tule takaisin */
    tarkista("jumiutunut lohko: aikaraja",
             pl022_siirto(spi, tx, rx, sizeof tx) == SPI_AIKARAJA);
    printf("%s\n", virheita ? "TESTIT EPAONNISTUIVAT" : "kaikki ok");
    return virheita != 0;
}
// @loppu testit
