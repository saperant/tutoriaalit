#include <stdio.h>

// Lukee asetukset ensimmäisestä löytyvästä tiedostosta.
int main(void)
{
    const char *polut[] = {"oma.conf", "yleinen.conf"};
    for (int i = 0; i < 2; ++i) {
        FILE *f = fopen(polut[i], "r");
        if (!f)
            continue;
        char rivi[64];
        if (fgets(rivi, sizeof rivi, f))
            printf("asetus tiedostosta %s: %s", polut[i], rivi);
        fclose(f);
        return 0;
    }
    puts("ei asetuksia");
    return 1;
}
