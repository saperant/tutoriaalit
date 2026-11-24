/* Semihosting: tuloste ja lopetus debuggerin (tässä QEMU) kautta. */
#ifndef SEMIHOST_H
#define SEMIHOST_H

#include <stdint.h>

void tulosta(const char *teksti);
void tulosta_luku(uint32_t luku);
_Noreturn void lopeta(int koodi);

#endif
