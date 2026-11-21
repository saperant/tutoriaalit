#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    char *puskuri = malloc(64);
    if (puskuri == nullptr) {
        return EXIT_FAILURE;
    }
    strcpy(puskuri, "tätä muistia ei koskaan vapauteta");
    fprintf(stderr, "%s\n", puskuri);
    puskuri = nullptr;   // ainoa osoitin muistiin katoaa: vuoto
}
