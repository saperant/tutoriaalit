/* Huoltotyökalun kehykset laitteelle. */
#ifndef KEHYS_H
#define KEHYS_H

#include <stddef.h>
#include <stdint.h>

#define KEHYS_KELLO  0x01u  /* data: aika_ms (u32, little endian) */
#define KEHYS_NIMI   0x02u  /* data: laitteen nimi */
#define KEHYS_LED    0x03u  /* data: LED-bitit (u8) */
#define KEHYS_NOLLAA 0x04u  /* ei dataa: tyhjennä loki */
#define KEHYS_KAIKU  0x05u  /* data lähetetään takaisin */

enum { KEHYS_OK = 0, KEHYS_LYHYT = -1, KEHYS_TARKISTE = -2,
       KEHYS_TUNTEMATON = -3, KEHYS_LIIAN_PITKA = -4 };

/* kehys: tyyppi, pituus, data, crc16 (ilman rajoja ja ESC-koodausta) */
int kasittele_kehys(const uint8_t *kehys, size_t n);
const char *laitteen_nimi(void);
uint32_t kellonaika(void);

#endif
