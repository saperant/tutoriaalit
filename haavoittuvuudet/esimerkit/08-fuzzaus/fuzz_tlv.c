/* libFuzzer-kohde: fuzzeri kutsuu funktiota miljoonia kertoja eri
 * syötteillä ja seuraa kattavuutta. */
#include "tlv.h"

// @alku kohde
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t koko);

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t koko)
{
    struct viesti viesti;
    (void)tlv_jasenna(data, koko, &viesti);
    return 0;                           /* muut arvot on varattu */
}
// @loppu kohde
