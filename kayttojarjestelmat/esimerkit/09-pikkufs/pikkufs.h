// Pikkufs: pieni Unix-tyyppinen tiedostojärjestelmä levykuvassa.
// Rakenne: superlohko, inode- ja lohkobittikartat, inodetaulu ja
// datalohkot. Hakemisto on tiedosto, joka sisältää nimi–inode-pareja.
#ifndef PIKKUFS_H
#define PIKKUFS_H

#include <stddef.h>
#include <stdint.h>

// @alku asettelu
enum {
    LOHKO = 512,                 // lohkon koko tavuina
    LOHKOJA = 128,               // levykuva 64 KiB
    INODEJA = 32,
    SUORIA = 10,                 // suorat lohko-osoittimet inodessa
    EPASUORIA = LOHKO / 4,       // osoittimia epäsuorassa lohkossa
    NIMI_MAKS = 28,
    JUURI = 1,                   // inode 0 = "ei inodea"
};
enum {                           // levyn lohkot
    SUPERLOHKO = 0,
    INODEKARTTA = 1,
    LOHKOKARTTA = 2,
    INODETAULU = 3,              // 32 inodea x 64 tavua = 4 lohkoa
    DATA_ALKU = 7,
};
enum { TAIKALUKU = 0x4b4b4950 };   // "PIKK"
enum { VAPAA = 0, TIEDOSTO = 1, HAKEMISTO = 2 };

typedef struct {
    uint32_t taikaluku, lohkoja, inodeja, data_alku;
} superlohko_t;

typedef struct {
    uint16_t tyyppi, linkkeja;
    uint32_t koko;               // tavuina
    uint32_t suorat[SUORIA];     // 0 = lohkoa ei ole varattu
    uint32_t epasuora;           // lohko, jossa lisää osoittimia
    uint32_t varattu[3];
} inode_t;
static_assert(sizeof(inode_t) == 64);

typedef struct {
    uint32_t inode;              // 0 = vapaa paikka
    char nimi[NIMI_MAKS];
} tietue_t;
static_assert(sizeof(tietue_t) == 32);
// @loppu asettelu

// @alku rajapinta
typedef struct {
    int fd;
    superlohko_t sl;
} levy_t;

// Virheessä funktiot palauttavat negatiivisen errno-arvon.
int pfs_alusta(const char *kuva);
int pfs_avaa(levy_t *l, const char *kuva);
void pfs_sulje(levy_t *l);
int pfs_mkdir(levy_t *l, const char *polku);
int pfs_kirjoita(levy_t *l, const char *polku, const void *data,
                 size_t n);
long pfs_lue(levy_t *l, const char *polku, void *puskuri, size_t maks);
int pfs_linkki(levy_t *l, const char *vanha, const char *uusi);
int pfs_poista(levy_t *l, const char *polku);
void pfs_listaa(levy_t *l, const char *polku);
void pfs_tilasto(levy_t *l);
int pfs_tarkista(levy_t *l, bool korjaa);
// @loppu rajapinta

#endif
