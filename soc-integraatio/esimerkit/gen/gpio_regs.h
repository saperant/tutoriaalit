/* Generoitu tiedostosta gpio.toml (gen/rekisterit.py). Älä muokkaa. */
/* Yleiskäyttöiset 8-bittiset tulot ja lähdöt */
#ifndef GPIO_REGS_H
#define GPIO_REGS_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    volatile uint32_t ULOS;  /* 0x000 rw */
    volatile const uint32_t SISAAN;  /* 0x004 ro */
    volatile uint32_t SALLI;  /* 0x008 rw */
    volatile uint32_t REUNAT;  /* 0x00c w1c */
} gpio_regs_t;

_Static_assert(offsetof(gpio_regs_t, ULOS) == 0x0, "ULOS");
_Static_assert(offsetof(gpio_regs_t, SISAAN) == 0x4, "SISAAN");
_Static_assert(offsetof(gpio_regs_t, SALLI) == 0x8, "SALLI");
_Static_assert(offsetof(gpio_regs_t, REUNAT) == 0xc, "REUNAT");

#define GPIO_ULOS_MASKI 0xFFu
#define GPIO_SISAAN_MASKI 0xFFu
#define GPIO_SALLI_MASKI 0xFFu
#define GPIO_REUNAT_MASKI 0xFFu

#endif /* GPIO_REGS_H */
