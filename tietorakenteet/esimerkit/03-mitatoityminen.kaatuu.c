// Osoitin dynaamisen taulukon sisään mitätöityy, kun taulukko kasvaa:
// realloc voi siirtää datan uuteen paikkaan ja vapauttaa vanhan.
// AddressSanitizer pysäyttää ohjelman, kun vanhaa muistia luetaan.
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    size_t kapasiteetti = 4, koko = 0;
    int *data = malloc(kapasiteetti * sizeof *data);
    if (data == nullptr) {
        return EXIT_FAILURE;
    }
    data[koko++] = 10;

    int *ensimmainen = &data[0];        // osoitin taulukon sisään
    for (int i = 1; i < 100; i++) {
        if (koko == kapasiteetti) {
            kapasiteetti *= 2;
            int *uusi = realloc(data, kapasiteetti * sizeof *uusi);
            if (uusi == nullptr) {
                free(data);
                return EXIT_FAILURE;
            }
            data = uusi;                // vanha muisti on vapautettu
        }
        data[koko++] = 10 * (i + 1);
    }
    printf("ensimmäinen: %d\n", *ensimmainen);   // vapautettua muistia
    free(data);
    return EXIT_SUCCESS;
}
