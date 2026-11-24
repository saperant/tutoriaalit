#include "tarkistus.h"

#include <errno.h>
#include <math.h>
#include <stdlib.h>

/* @alku crc */
uint32_t crc32_laske(const uint8_t *data, size_t n)
{
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++)
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}
/* @loppu crc */

/* @alku tilasto */
int tilasto_laske(const double *x, size_t n,
                  double *keskiarvo, double *hajonta)
{
    if (n == 0 || x == NULL || keskiarvo == NULL || hajonta == NULL) {
        errno = EINVAL;
        return -1;
    }
    double ka = 0.0, m2 = 0.0;   /* Welfordin algoritmi */
    for (size_t i = 0; i < n; i++) {
        double d = x[i] - ka;
        ka += d / (double)(i + 1);
        m2 += d * (x[i] - ka);
    }
    *keskiarvo = ka;
    *hajonta = n > 1 ? sqrt(m2 / (double)(n - 1)) : 0.0;
    return 0;
}
/* @loppu tilasto */

static uint32_t crc32_jatka(uint32_t crc, const uint8_t *data, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++)
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
    }
    return crc;
}

/* @alku paloittain */
int crc32_paloittain(const uint8_t *data, size_t n, size_t pala,
                     edistyminen_fn edistyminen, void *kayttaja,
                     uint32_t *tulos)
{
    if (pala == 0 || tulos == NULL) {
        errno = EINVAL;
        return -1;
    }
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t alku = 0; alku < n; alku += pala) {
        size_t koko = n - alku < pala ? n - alku : pala;
        crc = crc32_jatka(crc, data + alku, koko);
        if (edistyminen && edistyminen(alku + koko, n, kayttaja) != 0) {
            errno = ECANCELED;
            return -1;
        }
    }
    *tulos = ~crc;
    return 0;
}
/* @loppu paloittain */

/* @alku heksana */
char *heksana(const uint8_t *data, size_t n)
{
    static const char merkit[] = "0123456789abcdef";
    char *p = malloc(2 * n + 1);
    if (p == NULL)
        return NULL;
    for (size_t i = 0; i < n; i++) {
        p[2 * i] = merkit[data[i] >> 4];
        p[2 * i + 1] = merkit[data[i] & 0xF];
    }
    p[2 * n] = '\0';
    return p;
}

void heksana_vapauta(char *p)
{
    free(p);
}
/* @loppu heksana */
