/* Äänipuskurin varaus: näytteet kanavittain, 16 bittiä näytettä kohden. */
#include <stdckdint.h>
#include <stdint.h>
#include <stdlib.h>

int16_t *varaa_aani(size_t naytteet, size_t kanavat)
{
    size_t maara;
    if (ckd_mul(&maara, naytteet, kanavat)) {
        return NULL;
    }
    return calloc(maara, sizeof(int16_t));
}
