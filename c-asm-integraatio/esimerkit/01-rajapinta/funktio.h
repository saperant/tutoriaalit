// Yhteinen otsake C:lle ja assemblylle. Kääntäjä ajaa .S-tiedostot
// (iso S) C:n esikääntäjän läpi ja määrittelee silloin makron
// __ASSEMBLER__, joten sama tiedosto antaa C:lle prototyypit ja
// assemblylle makrot.
#ifndef FUNKTIO_H
#define FUNKTIO_H

#ifdef __ASSEMBLER__
// @alku makrot
// Funktion alku: näkyvä symboli, tyyppi funktio (debuggerit ja
// profiloijat tunnistavat sen) ja nimiö.
#define FUNKTIO(nimi) .globl nimi; .type nimi, @function; nimi:
// Funktion koko symbolitauluun.
#define LOPPU(nimi) .size nimi, . - nimi
// Pino ei tarvitse suoritusoikeutta (ks. luku 3).
#define PINO_EI_SUORITETTAVA .section .note.GNU-stack, "", @progbits
// Purkutiedot (.cfi-direktiivit) vain, jos CFI on määritelty.
#ifdef CFI
#define CFI_ALKU .cfi_startproc
#define CFI_LOPPU .cfi_endproc
#define PURKU(...) __VA_ARGS__
#else
#define CFI_ALKU
#define CFI_LOPPU
#define PURKU(...)
#endif
// @loppu makrot
#else
#include <stddef.h>
// @alku prototyyppi
// Palauttaa tavun c esiintymien määrän nollaan päättyvässä
// merkkijonossa s.
size_t laske(const char *s, char c);
// @loppu prototyyppi
#endif

#endif
