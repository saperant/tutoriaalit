// Ohjelma kaatuu, kun asetusta ei löydy: haku palauttaa NULLin, jota
// kutsuja ei tarkista.
#include <stdio.h>
#include <string.h>

struct asetus {
    const char *nimi;
    int arvo;
};

static struct asetus asetukset[] = {{"leveys", 80}, {"korkeus", 24}};

static struct asetus *hae(const char *nimi)
{
    for (size_t i = 0; i < sizeof asetukset / sizeof asetukset[0]; i++)
        if (strcmp(asetukset[i].nimi, nimi) == 0)
            return &asetukset[i];
    return NULL;
}

static int arvo(const char *nimi)
{
    return hae(nimi)->arvo;
}

int main(void)
{
    printf("leveys %d\n", arvo("leveys"));
    printf("syvyys %d\n", arvo("syvyys"));
    return 0;
}
