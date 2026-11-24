// LD_PRELOAD-kääre: kirjaa ohjelman fopen-kutsut ja laskee ne.
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdio.h>

// @alku kaare
static FILE *(*aito_fopen)(const char *, const char *);
static unsigned avauksia, epaonnistui;

FILE *fopen(const char *polku, const char *tila)
{
    if (!aito_fopen)                     // seuraava fopen hakujärjestyksessä
        aito_fopen = (FILE *(*)(const char *, const char *))
            dlsym(RTLD_NEXT, "fopen");
    FILE *f = aito_fopen(polku, tila);
    int virhe = errno;
    ++avauksia;
    if (!f)
        ++epaonnistui;
    fprintf(stderr, "[mittari] fopen(\"%s\", \"%s\") -> %s\n", polku, tila,
            f ? "ok" : "virhe");
    errno = virhe;                       // kääre ei saa muuttaa errnoa
    return f;
}

__attribute__((destructor))
static void yhteenveto(void)
{
    fprintf(stderr, "[mittari] avauksia %u, epäonnistui %u\n", avauksia,
            epaonnistui);
}
// @loppu kaare
