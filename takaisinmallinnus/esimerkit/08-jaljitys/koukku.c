// LD_PRELOAD-koukku: kirjaa strcmp-kutsujen argumentit ja kutsuu
// sitten oikeaa funktiota. Ks. Objektitiedostot, linkitys ja ABI,
// luku 10.
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>

// @alku koukku
int strcmp(const char *a, const char *b)
{
    static int (*oikea)(const char *, const char *);
    if (oikea == NULL) {
        oikea = (int (*)(const char *, const char *))dlsym(RTLD_NEXT,
                                                           "strcmp");
    }
    fprintf(stderr, "[koukku] strcmp(\"%s\", \"%s\")\n", a, b);
    return oikea(a, b);
}
// @loppu koukku
