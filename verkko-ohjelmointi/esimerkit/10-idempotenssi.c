// Idempotenssi: palvelin kirjaa talletuksen, mutta vastaus katoaa.
// Asiakas yrittää uudelleen. Ilman pyyntötunnistetta talletus kirjataan
// kahdesti; tunnisteen kanssa palvelin tunnistaa toiston ja palauttaa
// saman vastauksen.
#define _GNU_SOURCE
#include "verkko.h"

static uint16_t portti;
static int kuuntelija;

// @alku palvelin
typedef struct {
    char tunniste[32];
    long saldo;                          // vastaus, joka annettiin
} kasitelty;

static int palvelin(void *) {
    long saldo[2] = {};
    kasitelty muisti[16];                // tuotannossa: aikarajattu taulu
    int muistissa = 0;
    bool pudotettu[2] = {};
    for (;;) {
        int fd = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
        FILE *sisaan = fdopen(fd, "r");  // rivi kerrallaan, ks. luku 3
        char rivi[96], tunniste[32];
        int tili;
        long maara;
        if (fgets(rivi, sizeof rivi, sisaan) == nullptr ||
            sscanf(rivi, "TALLETA %d %31s %ld", &tili, tunniste, &maara) != 3
            || tili < 0 || tili > 1) {
            fclose(sisaan);
            return 0;                    // LOPETA tai virhe
        }
        long vastaus = -1;
        for (int i = 0; i < muistissa; i++) {
            if (strcmp(muisti[i].tunniste, tunniste) == 0) {
                vastaus = muisti[i].saldo;   // toisto: ei kirjata uudelleen
            }
        }
        if (vastaus == -1) {
            vastaus = saldo[tili] += maara;
            if (strcmp(tunniste, "-") != 0 && muistissa < 16) {
                muisti[muistissa++] = (kasitelty){.saldo = vastaus};
                snprintf(muisti[muistissa - 1].tunniste, 32, "%s", tunniste);
            }
        }
        if (!pudotettu[tili]) {          // vikaharjoitus: ensimmäinen
            pudotettu[tili] = true;      // vastaus katoaa matkalla
        } else {
            dprintf(fd, "SALDO %ld\n", vastaus);
        }
        fclose(sisaan);                  // sulkee myös fd:n
    }
}
// @loppu palvelin

// @alku asiakas
// Lähettää pyynnön ja yrittää uudelleen uudella yhteydellä, jos vastausta
// ei tule. Sama tunniste jokaisella yrityksellä.
static long talleta(int tili, const char *tunniste, long maara) {
    for (int yritys = 1; yritys <= 3; yritys++) {
        int fd = yhdista(portti);
        dprintf(fd, "TALLETA %d %s %ld\n", tili, tunniste, maara);
        FILE *sisaan = fdopen(fd, "r");
        char vastaus[32];
        long saldo;
        bool saatiin = fgets(vastaus, sizeof vastaus, sisaan) != nullptr &&
                       sscanf(vastaus, "SALDO %ld", &saldo) == 1;
        fclose(sisaan);
        if (saatiin) {
            return saldo;
        }
        printf("  yritys %d: ei vastausta, yritetään uudelleen\n", yritys);
    }
    return -1;
}
// @loppu asiakas

int main(void) {
    vahtikoira();
    kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(palvelin, nullptr);
    // @alku kaytto
    puts("talletus 10 ilman tunnistetta:");
    printf("  saldo %ld\n", talleta(0, "-", 10));
    puts("talletus 10 tunnisteella 7f3a-0001:");
    printf("  saldo %ld\n", talleta(1, "7f3a-0001", 10));
    // @loppu kaytto
    int fd = yhdista(portti);
    dprintf(fd, "LOPETA\n");
    close(fd);
    close(kuuntelija);
    return odota(pid);
}
