/* CRC-16 ja COBS. Sama koodi on isäntäkoneen Python-mallissa
 * (python/mallit/kehys.py), ja testi ajaa ne toisiaan vastaan. */
#include "kehys.h"

// @alku crc
uint16_t crc16(const uint8_t *data, size_t n) {
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < n; i++) {
        crc ^= (uint16_t)(data[i] << 8);
        for (int bitti = 0; bitti < 8; bitti++) {
            crc = (crc & 0x8000u) ? (uint16_t)(crc << 1 ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}
// @loppu crc

// @alku koodaa
/* Jokainen nollatavu korvataan etäisyydellä seuraavaan nollaan.
 * Lohkon ensimmäinen tavu (koodi) kertoo, montako tavua lohkossa on
 * koodi mukaan lukien; koodi 0xFF tarkoittaa 254 nollatonta tavua
 * ilman nollaa perässä. */
size_t cobs_koodaa(const uint8_t *data, size_t n, uint8_t *kohde) {
    size_t koodin_paikka = 0;
    size_t k = 1;
    uint8_t koodi = 1;
    for (size_t i = 0; i < n; i++) {
        if (data[i] != 0) {
            kohde[k++] = data[i];
            koodi++;
        }
        if (data[i] == 0 || koodi == 0xFFu) {
            kohde[koodin_paikka] = koodi;
            koodin_paikka = k++;
            koodi = 1;
        }
    }
    kohde[koodin_paikka] = koodi;
    return k;
}
// @loppu koodaa

// @alku pura
int cobs_pura(uint8_t *data, size_t n) {
    size_t luku = 0;
    size_t kirjoitus = 0;
    while (luku < n) {
        uint8_t koodi = data[luku++];
        if (koodi == 0 || luku + koodi - 1u > n) {
            return -1;
        }
        for (uint8_t i = 1; i < koodi; i++) {
            if (data[luku] == 0) {
                return -1;
            }
            data[kirjoitus++] = data[luku++];
        }
        if (koodi != 0xFFu && luku < n) {
            data[kirjoitus++] = 0; /* lohkon perässä oli nolla */
        }
    }
    return (int)kirjoitus;
}
// @loppu pura
