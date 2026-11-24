#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "raportti.h"
#include "testi.h"
#include "tilasto.h"

// @alku tilasto
static void keskiarvo_ja_hajonta(void)
{
    double x[] = {2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0};
    TARKISTA_LAHELLA(keskiarvo(x, 8), 5.0);
    TARKISTA_LAHELLA(keskihajonta(x, 8), sqrt(32.0 / 7.0));
}

static void mediaani_pariton_ja_parillinen(void)
{
    double pariton[] = {3.0, 1.0, 2.0};
    double parillinen[] = {4.0, 1.0, 3.0, 2.0};
    TARKISTA_LAHELLA(mediaani(pariton, 3), 2.0);
    TARKISTA_LAHELLA(mediaani(parillinen, 4), 2.5);
}
// @loppu tilasto

// @alku valekello
static void raportissa_on_aika_ja_luvut(void)
{
    double x[] = {1.0, 2.0, 6.0};
    char puskuri[128];
    FILE *ulos = fmemopen(puskuri, sizeof puskuri, "w");
    TARKISTA(kirjoita_raportti(ulos, x, 3) == 0);
    fclose(ulos);
    const char *odotettu =
        "raportti 2026-01-01 12:00 UTC: n=3 ka=3.00 md=2.00\n";
    TARKISTA(strcmp(puskuri, odotettu) == 0);
    TARKISTA(x[2] == 6.0); // sarja ei muuttunut
}
// @loppu valekello

// @alku wrap
// Linkkeri ohjaa malloc-kutsut tänne (-Wl,--wrap=malloc); aito malloc
// on __real_malloc. Testi voi pyytää seuraavan varauksen epäonnistumaan.
void *__real_malloc(size_t koko);
static bool malloc_epaonnistuu;

void *__wrap_malloc(size_t koko)
{
    if (malloc_epaonnistuu) {
        malloc_epaonnistuu = false;
        return NULL;
    }
    return __real_malloc(koko);
}

static void muistin_loppuminen_palauttaa_virheen(void)
{
    double x[] = {1.0};
    malloc_epaonnistuu = true;
    TARKISTA(kirjoita_raportti(stdout, x, 1) == -1);
}
// @loppu wrap

int main(void)
{
    const testi testit[] = {
        {"keskiarvo_ja_hajonta", keskiarvo_ja_hajonta},
        {"mediaani_pariton_ja_parillinen", mediaani_pariton_ja_parillinen},
        {"raportissa_on_aika_ja_luvut", raportissa_on_aika_ja_luvut},
        {"muistin_loppuminen_palauttaa_virheen",
         muistin_loppuminen_palauttaa_virheen},
    };
    return aja_testit(testit, (int)(sizeof testit / sizeof testit[0]));
}
