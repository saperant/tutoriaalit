// Kenttä lisätty keskelle: käännösaikainen tarkistus pysäyttää.
#include <stddef.h>
#include <stdint.h>
// @alku rikki
struct viesti {
    uint64_t aikaleima;
    uint32_t tarkiste;
    uint32_t lahettaja;  // uusi kenttä keskelle
    uint16_t pituus;
    uint8_t tyyppi;
    uint8_t varattu;
};
_Static_assert(sizeof(struct viesti) == 16, "viestin koko muuttui");
// @loppu rikki
