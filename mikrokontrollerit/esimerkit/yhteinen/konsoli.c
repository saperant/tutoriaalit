/* UART0-ajuri. Lähetys odottaa pollaamalla, että lähetysrekisteri
 * vapautuu; keskeytysohjattu vastaanotto on esimerkissä 07-rengas. */
#include <stdarg.h>
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

// @alku alusta
void konsoli_alusta(void) {
    UART0->BAUDDIV = KELLO_HZ / 115200u;   /* 217 */
    UART0->CTRL = UART_CTRL_TXEN | UART_CTRL_RXEN;
}

void konsoli_merkki(char merkki) {
    while (UART0->STATE & UART_STATE_TXFULL) {
        /* odota, että edellinen merkki on siirtynyt lähettimeen */
    }
    UART0->DATA = (uint8_t)merkki;
}
// @loppu alusta

void konsoli_kirjoita(const char *teksti) {
    while (*teksti != '\0') {
        konsoli_merkki(*teksti++);
    }
}

static void luku(uint32_t arvo, unsigned kanta, int leveys, char tayte) {
    char puskuri[12];
    int i = 0;
    do {
        unsigned numero = arvo % kanta;
        puskuri[i++] = (char)(numero < 10 ? '0' + numero : 'a' + numero - 10);
        arvo /= kanta;
    } while (arvo != 0);
    while (i < leveys && i < (int)sizeof puskuri) {
        puskuri[i++] = tayte;
    }
    while (i > 0) {
        konsoli_merkki(puskuri[--i]);
    }
}

void tulosta(const char *muoto, ...) {
    va_list argumentit;
    va_start(argumentit, muoto);
    for (const char *p = muoto; *p != '\0'; p++) {
        if (*p != '%') {
            konsoli_merkki(*p);
            continue;
        }
        p++;
        char tayte = ' ';
        int leveys = 0;
        if (*p == '0') {
            tayte = '0';
            p++;
        }
        while (*p >= '0' && *p <= '9') {
            leveys = leveys * 10 + (*p++ - '0');
        }
        switch (*p) {
        case 's':
            konsoli_kirjoita(va_arg(argumentit, const char *));
            break;
        case 'c':
            konsoli_merkki((char)va_arg(argumentit, int));
            break;
        case 'd': {
            int arvo = va_arg(argumentit, int);
            if (arvo < 0) {
                konsoli_merkki('-');
                luku(0u - (uint32_t)arvo, 10, leveys, tayte);
            } else {
                luku((uint32_t)arvo, 10, leveys, tayte);
            }
            break;
        }
        case 'u':
            luku(va_arg(argumentit, unsigned), 10, leveys, tayte);
            break;
        case 'x':
            luku(va_arg(argumentit, unsigned), 16, leveys, tayte);
            break;
        case '%':
            konsoli_merkki('%');
            break;
        default:
            konsoli_merkki('?');
            break;
        }
    }
    va_end(argumentit);
}
