// Laskurin arvo muuttuu jossain, missä sitä ei pitäisi muuttaa.
#include <stdio.h>

struct tila {
    char nimi[8];
    int laskuri;
};

static void nimea(struct tila *t, const char *uusi)
{
    for (int i = 0; uusi[i] != '\0'; i++)
        t->nimi[i] = uusi[i];       // ei rajatarkistusta
}

int main(void)
{
    struct tila t = {"alku", 0};
    for (int i = 0; i < 3; i++)
        t.laskuri++;
    nimea(&t, "mittari-7");
    printf("laskuri %d\n", t.laskuri);
    return 0;
}
