/* FORTIFY_SOURCE: kääntäjä tietää kohdepuskurin koon ja korvaa strcpy:n
 * tarkistavalla __strcpy_chk-versiolla. */
#include <stdio.h>
#include <string.h>

// @alku fortify
int main(int argc, char *argv[])
{
    char tunnus[8];
    strcpy(tunnus, argc > 1 ? argv[1] : "aino");  /* VIRHE: ei rajaa */
    printf("tunnus: %s\n", tunnus);
    return 0;
}
// @loppu fortify
