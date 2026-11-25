// Pikkufs:n toteutus. Kaikki levyhaku kulkee kahden funktion kautta
// (lue_lohko ja kirjoita_lohko), kuten ytimen lohkokerroksessa.
#define _GNU_SOURCE
#include "pikkufs.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// @alku lohkot
static void lue_lohko(const levy_t *l, uint32_t n, void *p) {
    if (pread(l->fd, p, LOHKO, (off_t)n * LOHKO) != LOHKO) {
        perror("pread");
        exit(EXIT_FAILURE);
    }
}

static void kirjoita_lohko(const levy_t *l, uint32_t n, const void *p) {
    if (pwrite(l->fd, p, LOHKO, (off_t)n * LOHKO) != LOHKO) {
        perror("pwrite");
        exit(EXIT_FAILURE);
    }
}
// @loppu lohkot

// @alku bitit
static bool bitti(const uint8_t *kartta, uint32_t i) {
    return kartta[i / 8] >> (i % 8) & 1;
}

static void aseta(uint8_t *kartta, uint32_t i, bool arvo) {
    kartta[i / 8] = (uint8_t)(arvo ? kartta[i / 8] | 1u << (i % 8)
                                   : kartta[i / 8] & ~(1u << (i % 8)));
}

// Etsii ensimmäisen vapaan bitin, varaa sen ja palauttaa sen numeron.
static uint32_t varaa_bitti(const levy_t *l, uint32_t kartta,
                            uint32_t maara) {
    uint8_t k[LOHKO];
    lue_lohko(l, kartta, k);
    for (uint32_t i = 0; i < maara; i++) {
        if (!bitti(k, i)) {
            aseta(k, i, true);
            kirjoita_lohko(l, kartta, k);
            return i;
        }
    }
    return 0;                            // bitti 0 on aina varattu
}

static void vapauta_bitti(const levy_t *l, uint32_t kartta, uint32_t i) {
    uint8_t k[LOHKO];
    lue_lohko(l, kartta, k);
    aseta(k, i, false);
    kirjoita_lohko(l, kartta, k);
}
// @loppu bitit

// @alku inodet
static void lue_inode(const levy_t *l, uint32_t n, inode_t *in) {
    inode_t taulu[LOHKO / sizeof(inode_t)];
    lue_lohko(l, INODETAULU + n / 8, taulu);
    *in = taulu[n % 8];
}

static void kirjoita_inode(const levy_t *l, uint32_t n,
                           const inode_t *in) {
    inode_t taulu[LOHKO / sizeof(inode_t)];
    lue_lohko(l, INODETAULU + n / 8, taulu);
    taulu[n % 8] = *in;
    kirjoita_lohko(l, INODETAULU + n / 8, taulu);
}

static uint32_t uusi_lohko(const levy_t *l) {
    uint32_t n = varaa_bitti(l, LOHKOKARTTA, LOHKOJA);
    if (n != 0) {
        uint8_t nollat[LOHKO] = {};
        kirjoita_lohko(l, n, nollat);
    }
    return n;
}

// @alku lohko
// Tiedoston k:nnen lohkon numero levyllä. Jos varaa on tosi, puuttuva
// lohko (ja tarvittaessa epäsuora lohko) varataan. 0 = ei lohkoa.
static uint32_t lohko(const levy_t *l, inode_t *in, uint32_t k,
                      bool varaa) {
    if (k < SUORIA) {
        if (in->suorat[k] == 0 && varaa) {
            in->suorat[k] = uusi_lohko(l);
        }
        return in->suorat[k];
    }
    k -= SUORIA;
    if (k >= EPASUORIA) {
        return 0;
    }
    if (in->epasuora == 0) {
        if (!varaa || (in->epasuora = uusi_lohko(l)) == 0) {
            return 0;
        }
    }
    uint32_t osoittimet[EPASUORIA];
    lue_lohko(l, in->epasuora, osoittimet);
    if (osoittimet[k] == 0 && varaa) {
        osoittimet[k] = uusi_lohko(l);
        kirjoita_lohko(l, in->epasuora, osoittimet);
    }
    return osoittimet[k];
}
// @loppu lohko
// @loppu inodet

// @alku data
static long lue_data(const levy_t *l, inode_t *in, uint32_t alku,
                     void *puskuri, size_t n) {
    if (alku >= in->koko) {
        return 0;
    }
    n = n < in->koko - alku ? n : in->koko - alku;
    uint8_t lohkodata[LOHKO];
    for (size_t tehty = 0; tehty < n;) {
        uint32_t kohta = alku + (uint32_t)tehty;
        size_t osa = LOHKO - kohta % LOHKO;
        osa = osa < n - tehty ? osa : n - tehty;
        uint32_t nro = lohko(l, in, kohta / LOHKO, false);
        if (nro == 0) {
            memset(lohkodata, 0, LOHKO);     // aukko: nollia
        } else {
            lue_lohko(l, nro, lohkodata);
        }
        memcpy((uint8_t *)puskuri + tehty, lohkodata + kohta % LOHKO, osa);
        tehty += osa;
    }
    return (long)n;
}

static long kirjoita_data(const levy_t *l, inode_t *in, uint32_t alku,
                          const void *data, size_t n) {
    uint8_t lohkodata[LOHKO];
    size_t tehty = 0;
    while (tehty < n) {
        uint32_t kohta = alku + (uint32_t)tehty;
        size_t osa = LOHKO - kohta % LOHKO;
        osa = osa < n - tehty ? osa : n - tehty;
        uint32_t nro = lohko(l, in, kohta / LOHKO, true);
        if (nro == 0) {
            break;                       // levy tai tiedosto täynnä
        }
        lue_lohko(l, nro, lohkodata);    // lue–muokkaa–kirjoita
        memcpy(lohkodata + kohta % LOHKO, (const uint8_t *)data + tehty,
               osa);
        kirjoita_lohko(l, nro, lohkodata);
        tehty += osa;
    }
    if (alku + tehty > in->koko) {
        in->koko = alku + (uint32_t)tehty;
    }
    return tehty == n ? (long)n : -ENOSPC;
}

static void vapauta_lohkot(const levy_t *l, inode_t *in) {
    for (int i = 0; i < SUORIA; i++) {
        if (in->suorat[i]) {
            vapauta_bitti(l, LOHKOKARTTA, in->suorat[i]);
        }
    }
    if (in->epasuora) {
        uint32_t osoittimet[EPASUORIA];
        lue_lohko(l, in->epasuora, osoittimet);
        for (int i = 0; i < EPASUORIA; i++) {
            if (osoittimet[i]) {
                vapauta_bitti(l, LOHKOKARTTA, osoittimet[i]);
            }
        }
        vapauta_bitti(l, LOHKOKARTTA, in->epasuora);
    }
    memset(in->suorat, 0, sizeof in->suorat);
    in->epasuora = 0;
    in->koko = 0;
}
// @loppu data

// @alku hakemisto
// @alku etsi
// Etsii nimen hakemistosta. Palauttaa inoden numeron tai 0.
static uint32_t etsi(const levy_t *l, inode_t *hak, const char *nimi,
                     uint32_t *paikka) {
    tietue_t t;
    for (uint32_t k = 0; k < hak->koko; k += sizeof t) {
        lue_data(l, hak, k, &t, sizeof t);
        if (t.inode != 0 && strncmp(t.nimi, nimi, NIMI_MAKS) == 0) {
            if (paikka) {
                *paikka = k;
            }
            return t.inode;
        }
    }
    return 0;
}
// @loppu etsi

static int lisaa_nimi(const levy_t *l, uint32_t hak_nro, const char *nimi,
                      uint32_t inode) {
    if (strlen(nimi) >= NIMI_MAKS) {
        return -ENAMETOOLONG;
    }
    inode_t hak;
    lue_inode(l, hak_nro, &hak);
    tietue_t t = {.inode = inode};
    strcpy(t.nimi, nimi);
    uint32_t k = 0;                      // ensimmäinen vapaa paikka
    for (tietue_t vanha; k < hak.koko; k += sizeof vanha) {
        lue_data(l, &hak, k, &vanha, sizeof vanha);
        if (vanha.inode == 0) {
            break;
        }
    }
    long r = kirjoita_data(l, &hak, k, &t, sizeof t);
    kirjoita_inode(l, hak_nro, &hak);
    return r < 0 ? (int)r : 0;
}

// Selvittää polun "/a/b/c" vanhemman ("/a/b") ja viimeisen osan ("c").
static int selvita(const levy_t *l, const char *polku, uint32_t *vanhempi,
                   char *nimi) {
    if (polku[0] != '/') {
        return -EINVAL;
    }
    uint32_t nyt = JUURI;
    const char *osa = polku + 1;
    for (const char *viiva; (viiva = strchr(osa, '/')) != nullptr;
         osa = viiva + 1) {
        char valiosa[NIMI_MAKS] = {};
        if (viiva - osa >= NIMI_MAKS) {
            return -ENAMETOOLONG;
        }
        memcpy(valiosa, osa, (size_t)(viiva - osa));
        inode_t hak;
        lue_inode(l, nyt, &hak);
        if (hak.tyyppi != HAKEMISTO) {
            return -ENOTDIR;
        }
        if ((nyt = etsi(l, &hak, valiosa, nullptr)) == 0) {
            return -ENOENT;
        }
    }
    inode_t hak;
    lue_inode(l, nyt, &hak);
    if (hak.tyyppi != HAKEMISTO) {
        return -ENOTDIR;
    }
    if (strlen(osa) >= NIMI_MAKS) {
        return -ENAMETOOLONG;
    }
    strcpy(nimi, osa);
    *vanhempi = nyt;
    return 0;
}

// Palauttaa polun inoden numeron tai negatiivisen virheen.
static long hae(const levy_t *l, const char *polku) {
    if (strcmp(polku, "/") == 0) {
        return JUURI;
    }
    uint32_t vanhempi;
    char nimi[NIMI_MAKS];
    int r = selvita(l, polku, &vanhempi, nimi);
    if (r < 0) {
        return r;
    }
    inode_t hak;
    lue_inode(l, vanhempi, &hak);
    uint32_t n = etsi(l, &hak, nimi, nullptr);
    return n ? (long)n : -ENOENT;
}
// @loppu hakemisto

// @alku alusta
int pfs_alusta(const char *kuva) {
    levy_t l = {.fd = open(kuva, O_RDWR | O_CREAT | O_TRUNC, 0644)};
    if (l.fd == -1) {
        return -errno;
    }
    uint8_t nollat[LOHKO] = {};
    for (uint32_t i = 0; i < LOHKOJA; i++) {
        kirjoita_lohko(&l, i, nollat);
    }
    uint8_t lohko0[LOHKO] = {};
    superlohko_t sl = {TAIKALUKU, LOHKOJA, INODEJA, DATA_ALKU};
    memcpy(lohko0, &sl, sizeof sl);
    kirjoita_lohko(&l, SUPERLOHKO, lohko0);

    uint8_t kartta[LOHKO] = {};
    aseta(kartta, 0, true);              // inode 0: varattu merkiksi
    kirjoita_lohko(&l, INODEKARTTA, kartta);
    for (uint32_t i = 0; i < DATA_ALKU; i++) {
        aseta(kartta, i, true);          // metatietolohkot käytössä
    }
    kirjoita_lohko(&l, LOHKOKARTTA, kartta);

    uint32_t juuri = varaa_bitti(&l, INODEKARTTA, INODEJA);
    inode_t in = {.tyyppi = HAKEMISTO, .linkkeja = 2};
    kirjoita_inode(&l, juuri, &in);
    lisaa_nimi(&l, juuri, ".", juuri);
    lisaa_nimi(&l, juuri, "..", juuri);  // juuren vanhempi on se itse
    close(l.fd);
    return 0;
}
// @loppu alusta

int pfs_avaa(levy_t *l, const char *kuva) {
    l->fd = open(kuva, O_RDWR);
    if (l->fd == -1) {
        return -errno;
    }
    uint8_t lohko0[LOHKO];
    lue_lohko(l, SUPERLOHKO, lohko0);
    memcpy(&l->sl, lohko0, sizeof l->sl);
    if (l->sl.taikaluku != TAIKALUKU) {
        close(l->fd);
        return -EINVAL;                  // ei pikkufs-levy
    }
    return 0;
}

void pfs_sulje(levy_t *l) {
    fsync(l->fd);
    close(l->fd);
    l->fd = -1;
}

// @alku luo
static long luo(const levy_t *l, const char *polku, uint16_t tyyppi) {
    uint32_t vanhempi;
    char nimi[NIMI_MAKS];
    int r = selvita(l, polku, &vanhempi, nimi);
    if (r < 0) {
        return r;
    }
    inode_t hak;
    lue_inode(l, vanhempi, &hak);
    if (etsi(l, &hak, nimi, nullptr)) {
        return -EEXIST;
    }
    uint32_t n = varaa_bitti(l, INODEKARTTA, INODEJA);
    if (n == 0) {
        return -ENOSPC;
    }
    inode_t in = {.tyyppi = tyyppi, .linkkeja = 1};
    kirjoita_inode(l, n, &in);
    if ((r = lisaa_nimi(l, vanhempi, nimi, n)) < 0) {
        vapauta_bitti(l, INODEKARTTA, n);
        return r;
    }
    return n;
}

int pfs_mkdir(levy_t *l, const char *polku) {
    long n = luo(l, polku, HAKEMISTO);
    if (n < 0) {
        return (int)n;
    }
    uint32_t vanhempi;
    char nimi[NIMI_MAKS];
    selvita(l, polku, &vanhempi, nimi);
    lisaa_nimi(l, (uint32_t)n, ".", (uint32_t)n);
    lisaa_nimi(l, (uint32_t)n, "..", vanhempi);
    inode_t in;
    lue_inode(l, (uint32_t)n, &in);
    in.linkkeja = 2;                     // nimi vanhemmassa ja "."
    kirjoita_inode(l, (uint32_t)n, &in);
    lue_inode(l, vanhempi, &in);
    in.linkkeja++;                       // lapsen ".." osoittaa tänne
    kirjoita_inode(l, vanhempi, &in);
    return 0;
}
// @loppu luo

// @alku kirjoita
int pfs_kirjoita(levy_t *l, const char *polku, const void *data,
                 size_t n) {
    long nro = hae(l, polku);
    if (nro == -ENOENT) {
        nro = luo(l, polku, TIEDOSTO);
    }
    if (nro < 0) {
        return (int)nro;
    }
    inode_t in;
    lue_inode(l, (uint32_t)nro, &in);
    if (in.tyyppi != TIEDOSTO) {
        return -EISDIR;
    }
    vapauta_lohkot(l, &in);              // korvataan koko sisältö
    long r = kirjoita_data(l, &in, 0, data, n);
    kirjoita_inode(l, (uint32_t)nro, &in);
    return r < 0 ? (int)r : 0;
}

long pfs_lue(levy_t *l, const char *polku, void *puskuri, size_t maks) {
    long nro = hae(l, polku);
    if (nro < 0) {
        return nro;
    }
    inode_t in;
    lue_inode(l, (uint32_t)nro, &in);
    if (in.tyyppi != TIEDOSTO) {
        return -EISDIR;
    }
    return lue_data(l, &in, 0, puskuri, maks);
}
// @loppu kirjoita

// @alku linkki
int pfs_linkki(levy_t *l, const char *vanha, const char *uusi) {
    long nro = hae(l, vanha);
    if (nro < 0) {
        return (int)nro;
    }
    inode_t in;
    lue_inode(l, (uint32_t)nro, &in);
    if (in.tyyppi == HAKEMISTO) {
        return -EPERM;                   // hakemistoille ei kovia linkkejä
    }
    uint32_t vanhempi;
    char nimi[NIMI_MAKS];
    int r = selvita(l, uusi, &vanhempi, nimi);
    if (r < 0) {
        return r;
    }
    inode_t hak;
    lue_inode(l, vanhempi, &hak);
    if (etsi(l, &hak, nimi, nullptr)) {
        return -EEXIST;
    }
    if ((r = lisaa_nimi(l, vanhempi, nimi, (uint32_t)nro)) < 0) {
        return r;
    }
    in.linkkeja++;
    kirjoita_inode(l, (uint32_t)nro, &in);
    return 0;
}

// @alku poista
int pfs_poista(levy_t *l, const char *polku) {
    uint32_t vanhempi, paikka;
    char nimi[NIMI_MAKS];
    int r = selvita(l, polku, &vanhempi, nimi);
    if (r < 0) {
        return r;
    }
    if (strcmp(nimi, ".") == 0 || strcmp(nimi, "..") == 0) {
        return -EINVAL;
    }
    inode_t hak, in;
    lue_inode(l, vanhempi, &hak);
    uint32_t nro = etsi(l, &hak, nimi, &paikka);
    if (nro == 0) {
        return -ENOENT;
    }
    lue_inode(l, nro, &in);
    if (in.tyyppi == HAKEMISTO) {
        tietue_t t;
        for (uint32_t k = 2 * sizeof t; k < in.koko; k += sizeof t) {
            lue_data(l, &in, k, &t, sizeof t);
            if (t.inode != 0) {
                return -ENOTEMPTY;
            }
        }
        in.linkkeja = 0;                 // nimi ja "." poistuvat
        hak.linkkeja--;                  // lapsen ".." poistuu
    } else {
        in.linkkeja--;
    }
    tietue_t tyhja = {};                 // 1. nimi pois hakemistosta
    kirjoita_data(l, &hak, paikka, &tyhja, sizeof tyhja);
    kirjoita_inode(l, vanhempi, &hak);
    if (in.linkkeja == 0) {              // 2. viimeinen nimi: vapautus
        vapauta_lohkot(l, &in);
        in.tyyppi = VAPAA;
        vapauta_bitti(l, INODEKARTTA, nro);
    }
    kirjoita_inode(l, nro, &in);
    return 0;
}
// @loppu poista
// @loppu linkki

void pfs_listaa(levy_t *l, const char *polku) {
    long nro = hae(l, polku);
    printf("%s:\n", polku);
    if (nro < 0) {
        printf("  virhe %ld\n", nro);
        return;
    }
    inode_t hak;
    lue_inode(l, (uint32_t)nro, &hak);
    tietue_t t;
    for (uint32_t k = 0; k < hak.koko; k += sizeof t) {
        lue_data(l, &hak, k, &t, sizeof t);
        if (t.inode == 0) {
            continue;
        }
        inode_t in;
        lue_inode(l, t.inode, &in);
        printf("  %-14s inode %2u  %s  linkkejä %u  %5u tavua\n", t.nimi,
               t.inode, in.tyyppi == HAKEMISTO ? "hak" : "tds",
               in.linkkeja, in.koko);
    }
}

void pfs_tilasto(levy_t *l) {
    uint8_t ik[LOHKO], lk[LOHKO];
    lue_lohko(l, INODEKARTTA, ik);
    lue_lohko(l, LOHKOKARTTA, lk);
    int inodeja = 0, lohkoja = 0;
    for (uint32_t i = 1; i < INODEJA; i++) {
        inodeja += !bitti(ik, i);
    }
    for (uint32_t i = DATA_ALKU; i < LOHKOJA; i++) {
        lohkoja += !bitti(lk, i);
    }
    printf("vapaana: %d/%d inodea, %d/%d datalohkoa\n", inodeja,
           INODEJA - 1, lohkoja, LOHKOJA - DATA_ALKU);
}

// @alku tarkista
// fsck: käydään hakemistopuu läpi, lasketaan viittaukset inodeihin ja
// merkitään käytetyt lohkot. Tulosta verrataan bittikarttoihin.
typedef struct {
    int viittauksia[INODEJA];
    bool kaytossa[LOHKOJA];
} laskenta_t;

// @alku kaylapi
static void merkitse(const levy_t *l, inode_t *in, laskenta_t *k) {
    for (uint32_t i = 0; i * LOHKO < in->koko; i++) {
        uint32_t n = lohko(l, in, i, false);
        if (n) {
            k->kaytossa[n] = true;
        }
    }
    if (in->epasuora) {
        k->kaytossa[in->epasuora] = true;
    }
}

static void kay_lapi(const levy_t *l, uint32_t nro, laskenta_t *k) {
    inode_t hak;
    lue_inode(l, nro, &hak);
    merkitse(l, &hak, k);
    tietue_t t;
    for (uint32_t p = 0; p < hak.koko; p += sizeof t) {
        lue_data(l, &hak, p, &t, sizeof t);
        if (t.inode == 0 || t.inode >= INODEJA) {
            continue;
        }
        if (k->viittauksia[t.inode]++ > 0) {
            continue;                    // jo käsitelty
        }
        inode_t in;
        lue_inode(l, t.inode, &in);
        if (in.tyyppi == HAKEMISTO) {
            kay_lapi(l, t.inode, k);
        } else {
            merkitse(l, &in, k);
        }
    }
}

// @loppu kaylapi

int pfs_tarkista(levy_t *l, bool korjaa) {
    laskenta_t k = {};
    for (uint32_t i = 0; i < DATA_ALKU; i++) {
        k.kaytossa[i] = true;
    }
    k.viittauksia[JUURI] = 1;            // juuri on aina olemassa
    kay_lapi(l, JUURI, &k);
    k.viittauksia[JUURI]--;

    uint8_t ik[LOHKO], lk[LOHKO];
    lue_lohko(l, INODEKARTTA, ik);
    lue_lohko(l, LOHKOKARTTA, lk);
    int virheita = 0;
    // @alku vertailu
    for (uint32_t i = 1; i < INODEJA; i++) {
        inode_t in;
        lue_inode(l, i, &in);
        if (k.viittauksia[i] > 0 && in.linkkeja != k.viittauksia[i]) {
            printf("  inode %u: linkkejä %u, viittauksia %d\n", i,
                   in.linkkeja, k.viittauksia[i]);
            in.linkkeja = (uint16_t)k.viittauksia[i];
            if (korjaa) {
                kirjoita_inode(l, i, &in);
            }
            virheita++;
        }
        if (bitti(ik, i) != (k.viittauksia[i] > 0)) {
            printf("  inode %u: bittikartta %d, käytössä %d\n", i,
                   bitti(ik, i), k.viittauksia[i] > 0);
            aseta(ik, i, k.viittauksia[i] > 0);
            virheita++;
        }
    }
    // @loppu vertailu
    for (uint32_t i = DATA_ALKU; i < LOHKOJA; i++) {
        if (bitti(lk, i) != k.kaytossa[i]) {
            printf("  lohko %u: bittikartta %d, käytössä %d\n", i,
                   bitti(lk, i), k.kaytossa[i]);
            aseta(lk, i, k.kaytossa[i]);
            virheita++;
        }
    }
    if (korjaa) {
        kirjoita_lohko(l, INODEKARTTA, ik);
        kirjoita_lohko(l, LOHKOKARTTA, lk);
    }
    return virheita;
}
// @loppu tarkista
