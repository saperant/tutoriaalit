#include <string.h>
#include <strings.h>

// @alku versiot
// Vanha toiminta säilyy versiona TUNNUS_1 jo käännetyille ohjelmille.
__attribute__((symver("vertaa_tunnus@TUNNUS_1")))
int vertaa_tunnus_v1(const char *a, const char *b)
{
    return strcasecmp(a, b) == 0;
}

// Uusi toiminta (kirjainkoko merkitsee) on oletusversio TUNNUS_2.
__attribute__((symver("vertaa_tunnus@@TUNNUS_2")))
int vertaa_tunnus_v2(const char *a, const char *b)
{
    return strcmp(a, b) == 0;
}
// @loppu versiot
