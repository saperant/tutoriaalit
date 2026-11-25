#include <stdio.h>
#include <stdlib.h>

// @alku lue
// Lukee tiedostosta enintään n kokonaislukua. Palauttaa taulukon, jonka
// kutsuja vapauttaa, tai nullptr, jos lukeminen epäonnistui.
int *lue_luvut(const char *polku, size_t n, size_t *luettu)
{
    int *luvut = malloc(n * sizeof *luvut);
    if (luvut == nullptr) {
        return nullptr;
    }
    FILE *f = fopen(polku, "r");
    if (f == nullptr) {
        return nullptr;   // virhe: luvut jää vapauttamatta
    }
    *luettu = 0;
    while (*luettu < n && fscanf(f, "%d", &luvut[*luettu]) == 1) {
        ++*luettu;
    }
    fclose(f);
    return luvut;
}
// @loppu lue

int main(void)
{
    FILE *f = fopen("luvut.txt", "w");
    if (f == nullptr) {
        return EXIT_FAILURE;
    }
    fprintf(f, "3 1 4 1 5\n");
    if (fclose(f) != 0) {
        return EXIT_FAILURE;
    }

    size_t n = 0;
    int *luvut = lue_luvut("luvut.txt", 8, &n);
    if (luvut == nullptr) {
        return EXIT_FAILURE;
    }
    int summa = 0;
    for (size_t i = 0; i < n; ++i) {
        summa += luvut[i];
    }
    printf("luettiin %zu lukua, summa %d\n", n, summa);
    free(luvut);
    remove("luvut.txt");
}
