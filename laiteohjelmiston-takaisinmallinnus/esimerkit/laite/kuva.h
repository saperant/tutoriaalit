/* Sovelluksen otsake flashissa. Käynnistyslatain tarkistaa sen ennen
 * kuin se hyppää sovellukseen. */
#ifndef KUVA_H
#define KUVA_H

#include <stdint.h>

#define SOVELLUS_OTSAKE 0x00010000u /* otsake */
#define SOVELLUS_ALKU   0x00010100u /* sovelluksen vektoritaulu */
#define SOVELLUS_MAKS   0x0002EF00u /* tilaa asetuslohkoon asti */
#define LAITETUNNUS     0x4C540064u /* "LT" ja malli 100 */

typedef struct {
    uint32_t taikaluku;      /* "LTAP" */
    uint32_t laitetunnus;
    uint32_t versio;         /* 0x00MMmmpp */
    uint32_t pituus;         /* sovelluksen tavut */
    uint32_t crc32;          /* sovelluksen CRC-32 */
    uint32_t allekirjoitus;  /* allekirjoituksen pituus, 0 = ei ole */
} sovellus_otsake_t;

#define OTSAKE_TAIKALUKU 0x5041544Cu /* "LTAP" muistissa */

enum {
    KUVA_OK = 0,
    KUVA_TAIKALUKU,
    KUVA_LAITE,
    KUVA_PITUUS,
    KUVA_TARKISTE,
    KUVA_ALLEKIRJOITUS,
};

int kuva_kelpaa(const sovellus_otsake_t *otsake);

#endif
