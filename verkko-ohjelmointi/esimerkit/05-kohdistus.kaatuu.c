// Virhe: puskurin keskeltä luetaan osoitintyyppimuunnoksella. Osoite ei
// ole jaollinen neljällä, mikä on C:ssä määrittelemätöntä käytöstä
// (UBSan: misaligned address). Oikein: memcpy tai lue_u32.
#include <arpa/inet.h>
#include <stdint.h>
#include <stdio.h>

int main(void) {
    // @alku virhe
    alignas(4) uint8_t viesti[8] = {7, 0x00, 0x00, 0x01, 0x2c};
    uint32_t pituus = ntohl(*(const uint32_t *)(viesti + 1));  // VÄÄRIN
    // @loppu virhe
    printf("pituus %u\n", pituus);
    return 0;
}
