/* Käynnistys: ohjelma tunnistaa SoC:n ja kokeilee oheislaitteita. */
#include <stdint.h>

#include "soc.h"
#include "tuki.h"

static void tunniste(uint32_t arvo)
{
    char merkit[5];
    for (int i = 0; i < 4; i++) merkit[i] = (char)(arvo >> (24 - 8 * i));
    merkit[4] = '\0';
    tulosta(merkit);
}

int main(void)
{
    tulosta("Pikku-SoC käynnistyi\n");

    /* @alku tunnistus */
    uint32_t id = SYSCON->TUNNISTE;
    tulosta("tunniste: ");
    tulosta_hex(id);
    tulosta(" (");
    tunniste(id);
    tulosta(")\nmisa:     ");
    tulosta_hex(csr_lue(misa));
    tulosta("\n");
    /* @loppu tunnistus */

    /* @alku apurekisteri */
    SYSCON->APU = 0xC0FFEEu;
    tulosta("APU:      ");
    tulosta_hex(SYSCON->APU);
    tulosta("\n");
    /* @loppu apurekisteri */

    /* @alku jaksot */
    uint32_t alku = csr_lue(mcycle);
    uint32_t mtime = CLINT->MTIME_L;
    uint32_t loppu = csr_lue(mcycle);
    tulosta("CLINT-luku kesti ");
    tulosta_luku(loppu - alku);
    tulosta(" jaksoa, mtime = ");
    tulosta_luku(mtime);
    tulosta("\n");
    /* @loppu jaksot */
    return 0;
}
