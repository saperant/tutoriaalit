/* Konsoli ja lopetus isäntäkoneella: sama rajapinta kuin
 * ../yhteinen/konsoli.c ja ../yhteinen/semihost.c. */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

#include "konsoli.h"
#include "semihost.h"

void konsoli_alusta(void) {}

void konsoli_merkki(char merkki) {
    putchar(merkki);
}

void konsoli_kirjoita(const char *teksti) {
    fputs(teksti, stdout);
}

void tulosta(const char *muoto, ...) {
    va_list argumentit;
    va_start(argumentit, muoto);
    vprintf(muoto, argumentit);
    va_end(argumentit);
}

_Noreturn void lopeta(int koodi) {
    fflush(stdout);
    exit(koodi);
}
