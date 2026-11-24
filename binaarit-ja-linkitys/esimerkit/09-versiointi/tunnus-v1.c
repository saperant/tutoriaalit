#include <strings.h>

// Kirjaston ensimmäinen julkaisu: tunnuksen vertailu ei erota
// isoja ja pieniä kirjaimia.
int vertaa_tunnus(const char *a, const char *b)
{
    return strcasecmp(a, b) == 0;
}
