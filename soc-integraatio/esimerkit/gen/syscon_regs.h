/* Generoitu tiedostosta syscon.json (gen/rekisterit.py). Älä muokkaa. */
/* Järjestelmäohjain: tunniste, apurekisteri ja lopetus */
#ifndef SYSCON_REGS_H
#define SYSCON_REGS_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    volatile const uint32_t TUNNISTE;  /* 0x000 vakio */
    volatile uint32_t APU;  /* 0x004 rw */
    volatile uint32_t LOPETA;  /* 0x008 wo */
} syscon_regs_t;

_Static_assert(offsetof(syscon_regs_t, TUNNISTE) == 0x0, "TUNNISTE");
_Static_assert(offsetof(syscon_regs_t, APU) == 0x4, "APU");
_Static_assert(offsetof(syscon_regs_t, LOPETA) == 0x8, "LOPETA");

#define SYSCON_TUNNISTE_MASKI 0xFFFFFFFFu
#define SYSCON_APU_MASKI 0xFFFFFFFFu
#define SYSCON_LOPETA_MASKI 0xFFu

#endif /* SYSCON_REGS_H */
