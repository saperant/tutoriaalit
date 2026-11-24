/* Taulukon solujen varaus: rivit kertaa sarakkeet osoitinta. */
#include <stdlib.h>

char **varaa_solut(unsigned rivit, unsigned sarakkeet)
{
    size_t koko = rivit * sarakkeet * sizeof(char *);
    return malloc(koko);
}
