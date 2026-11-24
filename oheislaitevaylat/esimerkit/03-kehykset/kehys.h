/* Kehystys tavuvirrassa: CRC-16 ja COBS (Consistent Overhead Byte
 * Stuffing). Kehys on COBS(hyötykuorma + CRC) ja sen perässä 0x00. */
#ifndef KEHYS_H
#define KEHYS_H

#include <stddef.h>
#include <stdint.h>

// @alku rajapinta
#define KEHYS_EROTIN 0x00u

/* CRC-16/CCITT-FALSE: polynomi 0x1021, alkuarvo 0xFFFF. */
uint16_t crc16(const uint8_t *data, size_t n);

/* Koodaa n tavua kohteeseen, jossa on tilaa n + n / 254 + 1 tavua.
 * Tuloksessa ei ole nollatavuja. Palauttaa pituuden. */
size_t cobs_koodaa(const uint8_t *data, size_t n, uint8_t *kohde);

/* Purkaa paikallaan. Palauttaa puretun pituuden tai -1, jos data ei
 * ole kelvollista COBSia (nolla datassa tai liian pitkä hyppy). */
int cobs_pura(uint8_t *data, size_t n);
// @loppu rajapinta

#endif
