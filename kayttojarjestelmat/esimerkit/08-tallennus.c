// Tiedoston atominen korvaaminen: kirjoitetaan väliaikaiseen
// tiedostoon, fsync, rename ja lopuksi hakemiston fsync.
#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>

#include "tarkista.h"

// @alku tallenna
// Kaatuminen missä kohdassa tahansa jättää joko vanhan tai uuden
// sisällön, ei koskaan puolikasta.
static int tallenna(const char *hakemisto, const char *nimi,
                    const char *data, size_t n) {
    char tilapainen[256], lopullinen[256];
    snprintf(tilapainen, sizeof tilapainen, "%s/.%s.tmp", hakemisto, nimi);
    snprintf(lopullinen, sizeof lopullinen, "%s/%s", hakemisto, nimi);

    int fd = open(tilapainen, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd == -1) {
        return -1;
    }
    for (size_t kirjoitettu = 0; kirjoitettu < n;) {
        ssize_t k = write(fd, data + kirjoitettu, n - kirjoitettu);
        if (k == -1) {                   // osittainen kirjoitus on
            close(fd);                   // mahdollinen: silmukka
            unlink(tilapainen);
            return -1;
        }
        kirjoitettu += (size_t)k;
    }
    if (fsync(fd) == -1 || close(fd) == -1) {   // data levylle
        unlink(tilapainen);
        return -1;
    }
    if (rename(tilapainen, lopullinen) == -1) { // atominen vaihto
        unlink(tilapainen);
        return -1;
    }
    int hak = open(hakemisto, O_RDONLY | O_DIRECTORY);
    if (hak == -1) {
        return -1;
    }
    int tulos = fsync(hak);              // uusi nimi levylle
    close(hak);
    return tulos;
}
// @loppu tallenna

int main(void) {
    // @alku kaytto
    const char *versiot[] = {"versio 1\n", "versio 2, pidempi\n"};
    for (int i = 0; i < 2; i++) {
        TARKISTA(tallenna(".", "asetukset.txt", versiot[i],
                          strlen(versiot[i])));
        char luettu[64] = {};
        int fd = TARKISTA(open("asetukset.txt", O_RDONLY));
        TARKISTA(read(fd, luettu, sizeof luettu - 1));
        TARKISTA(close(fd));
        printf("asetukset.txt: %s", luettu);
    }
    printf("väliaikainen jäi: %s\n",
           access(".asetukset.txt.tmp", F_OK) == 0 ? "kyllä" : "ei");
    // @loppu kaytto
    return 0;
}
