/* C-rajapinta C++-kirjastolle: läpinäkymätön kahva, virhekoodit eikä
   yhtään C++-tyyppiä tai poikkeusta rajapinnassa. */
#ifndef SUODATIN_H
#define SUODATIN_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* @alku rajapinta */
#define SUODATIN_API_VERSIO 1

/* Kirjasto käännetään -fvisibility=hidden, joten julkiset funktiot
   merkitään näkyviksi erikseen. */
#if defined(_WIN32)
#define SUODATIN_API __declspec(dllexport)
#else
#define SUODATIN_API __attribute__((visibility("default")))
#endif

typedef struct suodatin suodatin;   /* sisältö piilossa */

typedef enum {
    SUODATIN_OK = 0,
    SUODATIN_VIRHEELLINEN_ARGUMENTTI = 1,
    SUODATIN_MUISTI_LOPPUI = 2,
    SUODATIN_SISAINEN_VIRHE = 3,
} suodatin_tila;

SUODATIN_API int suodatin_api_versio(void);
SUODATIN_API suodatin_tila suodatin_luo(size_t ikkuna,
                                        suodatin **tulos);
SUODATIN_API suodatin_tila suodatin_syota(suodatin *s,
                                          const double *sisaan,
                                          double *ulos, size_t n);
SUODATIN_API void suodatin_tuhoa(suodatin *s);   /* NULL sallittu */
SUODATIN_API const char *suodatin_virheviesti(suodatin_tila tila);
/* @loppu rajapinta */

#ifdef __cplusplus
}
#endif

#endif
