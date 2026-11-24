// Säie asiakasta kohden: jokainen yhteys saa irrotetun säikeen. Säikeet
// jakavat avain-arvo-varaston, jota suojaa mutex. Pääsäie odottaa
// ehtomuuttujalla, että kaikki käsittelijät ovat valmiita.
// TSAN
#define _GNU_SOURCE
#include <pthread.h>

#include "verkko.h"

enum { ASIAKKAITA = 4, PYYNTOJA = 250, AVAIMIA = 8 };
static uint16_t portti;

// @alku varasto
static struct {
    pthread_mutex_t lukko;
    int maara;
    char avain[AVAIMIA][16];
    long arvo[AVAIMIA];
} varasto = {.lukko = PTHREAD_MUTEX_INITIALIZER};

// Lisää arvoon n ja palauttaa uuden arvon (tai -1, jos varasto on täynnä).
static long lisaa(const char *avain, long n) {
    pthread_mutex_lock(&varasto.lukko);
    int i = 0;
    while (i < varasto.maara && strcmp(varasto.avain[i], avain) != 0) {
        i++;
    }
    long tulos = -1;
    if (i < AVAIMIA) {
        if (i == varasto.maara) {
            snprintf(varasto.avain[i], 16, "%s", avain);
            varasto.maara++;
        }
        tulos = varasto.arvo[i] += n;
    }
    pthread_mutex_unlock(&varasto.lukko);
    return tulos;
}
// @loppu varasto

// @alku kasittelija
static pthread_mutex_t tila_lukko = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t valmis = PTHREAD_COND_INITIALIZER;
static int aktiivisia;                   // käynnissä olevat käsittelijät

static void *kasittele(void *arg) {
    int fd = *(int *)arg;
    free(arg);                           // säie omistaa argumenttinsa
    FILE *sisaan = fdopen(fd, "r");
    FILE *ulos = fdopen(dup(fd), "w");
    char rivi[64], avain[16];
    long n;
    while (fgets(rivi, sizeof rivi, sisaan) != nullptr) {
        if (sscanf(rivi, "LISAA %15s %ld", avain, &n) == 2) {
            fprintf(ulos, "OK %ld\n", lisaa(avain, n));
        } else {
            fprintf(ulos, "VIRHE tuntematon komento\n");
        }
        fflush(ulos);
    }
    fclose(ulos);
    fclose(sisaan);
    pthread_mutex_lock(&tila_lukko);
    if (--aktiivisia == 0) {
        pthread_cond_signal(&valmis);
    }
    pthread_mutex_unlock(&tila_lukko);
    return nullptr;
}
// @loppu kasittelija

// @alku hyvaksy
static void *hyvaksy(void *arg) {
    int kuuntelija = *(int *)arg;
    for (int i = 0; i < ASIAKKAITA; i++) {
        int *fd = (int *)malloc(sizeof *fd);
        *fd = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
        pthread_mutex_lock(&tila_lukko);
        aktiivisia++;
        pthread_mutex_unlock(&tila_lukko);
        pthread_t saie;
        pthread_attr_t asetukset;
        pthread_attr_init(&asetukset);
        pthread_attr_setdetachstate(&asetukset, PTHREAD_CREATE_DETACHED);
        if (pthread_create(&saie, &asetukset, kasittele, fd) != 0) {
            abort();                     // tuotannossa: sulje yhteys
        }
        pthread_attr_destroy(&asetukset);
    }
    return nullptr;
}
// @loppu hyvaksy

static void *asiakas(void *arg) {
    int nro = (int)(intptr_t)arg;
    FILE *sisaan = fdopen(yhdista(portti), "r");
    FILE *ulos = fdopen(dup(fileno(sisaan)), "w");
    char rivi[64];
    for (int i = 0; i < PYYNTOJA; i++) {
        fprintf(ulos, "LISAA yhteinen 1\nLISAA oma%d 2\n", nro);
        fflush(ulos);
        for (int j = 0; j < 2; j++) {
            if (fgets(rivi, sizeof rivi, sisaan) == nullptr ||
                strncmp(rivi, "OK ", 3) != 0) {
                abort();
            }
        }
    }
    fclose(ulos);
    fclose(sisaan);
    return nullptr;
}

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    pthread_t hyvaksyja, asiakkaat[ASIAKKAITA];
    pthread_create(&hyvaksyja, nullptr, hyvaksy, &kuuntelija);
    for (int i = 0; i < ASIAKKAITA; i++) {
        pthread_create(&asiakkaat[i], nullptr, asiakas, (void *)(intptr_t)i);
    }
    for (int i = 0; i < ASIAKKAITA; i++) {
        pthread_join(asiakkaat[i], nullptr);
    }
    pthread_join(hyvaksyja, nullptr);
    // @alku odota
    pthread_mutex_lock(&tila_lukko);
    while (aktiivisia > 0) {             // silmukka: valeherätykset
        pthread_cond_wait(&valmis, &tila_lukko);
    }
    pthread_mutex_unlock(&tila_lukko);
    // @loppu odota
    const char *avaimet[] = {"yhteinen", "oma0", "oma1", "oma2", "oma3"};
    for (int i = 0; i < 5; i++) {        // lisaa(a, 0) lukee arvon
        printf("%-8s %ld\n", avaimet[i], lisaa(avaimet[i], 0));
    }
    close(kuuntelija);
    return 0;
}
