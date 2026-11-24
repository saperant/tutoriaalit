// Pikkufs-esittely: levykuvan alustus, tiedostot ja hakemistot,
// uudelleenliitos sekä kaatumisen jälkeinen tarkistus.
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "pikkufs.h"

// @alku tulos
static void tulos(const char *mita, int r) {
    int leveys = 34;                     // UTF-8: jatkotavut eivät näy
    for (const char *c = mita; *c; c++) {
        leveys += (*c & 0xC0) == 0x80;
    }
    printf("%-*s %s\n", leveys, mita, r == 0 ? "ok" : strerrorname_np(-r));
}
// @loppu tulos

int main(void) {
    // @alku kaytto
    tulos("alusta levy.img", pfs_alusta("levy.img"));
    levy_t l;
    tulos("liitä", pfs_avaa(&l, "levy.img"));
    tulos("mkdir /docs", pfs_mkdir(&l, "/docs"));
    const char *teksti = "Ydin hallitsee laitteistoa.\n";
    tulos("kirjoita /docs/muistio.txt",
          pfs_kirjoita(&l, "/docs/muistio.txt", teksti, strlen(teksti)));
    static char iso[6000];               // 12 lohkoa: epäsuora tarvitaan
    for (size_t i = 0; i < sizeof iso; i++) {
        iso[i] = (char)('a' + i % 26);
    }
    tulos("kirjoita /iso.bin (6000 tavua)",
          pfs_kirjoita(&l, "/iso.bin", iso, sizeof iso));
    tulos("linkki /docs/muistio.txt /m",
          pfs_linkki(&l, "/docs/muistio.txt", "/m"));
    pfs_listaa(&l, "/");
    pfs_listaa(&l, "/docs");
    pfs_tilasto(&l);
    pfs_sulje(&l);
    // @loppu kaytto

    // @alku uudelleen
    tulos("liitä uudelleen", pfs_avaa(&l, "levy.img"));
    char puskuri[8192] = {};
    long n = pfs_lue(&l, "/m", puskuri, sizeof puskuri);
    printf("/m (%ld tavua): %s", n, puskuri);
    n = pfs_lue(&l, "/iso.bin", puskuri, sizeof puskuri);
    printf("/iso.bin: %ld tavua, sisältö %s\n", n,
           n == sizeof iso && memcmp(puskuri, iso, sizeof iso) == 0
               ? "sama" : "eri");
    // @loppu uudelleen

    // @alku virheet
    tulos("mkdir /docs", pfs_mkdir(&l, "/docs"));
    tulos("poista /docs", pfs_poista(&l, "/docs"));
    tulos("lue /ei-ole", (int)pfs_lue(&l, "/ei-ole", puskuri, 1));
    tulos("kirjoita /m/x", pfs_kirjoita(&l, "/m/x", "x", 1));
    tulos("linkki /docs /d2", pfs_linkki(&l, "/docs", "/d2"));
    // @loppu virheet

    // @alku poisto
    tulos("poista /docs/muistio.txt", pfs_poista(&l, "/docs/muistio.txt"));
    tulos("poista /docs", pfs_poista(&l, "/docs"));
    tulos("poista /iso.bin", pfs_poista(&l, "/iso.bin"));
    pfs_listaa(&l, "/");
    pfs_tilasto(&l);
    printf("tarkistus: %d virhettä\n", pfs_tarkista(&l, false));
    // @loppu poisto

    // @alku kaatuminen
    // Simuloidaan kaatumista: lohko on merkitty varatuksi, mutta inode
    // ei koskaan saanut sitä, ja linkkilaskuri jäi päivittämättä.
    uint8_t kartta[LOHKO];
    pread(l.fd, kartta, LOHKO, LOHKOKARTTA * LOHKO);
    kartta[100 / 8] |= 1 << (100 % 8);
    pwrite(l.fd, kartta, LOHKO, LOHKOKARTTA * LOHKO);
    inode_t taulu[LOHKO / sizeof(inode_t)];
    pread(l.fd, taulu, LOHKO, INODETAULU * LOHKO);
    taulu[JUURI].linkkeja = 7;
    pwrite(l.fd, taulu, LOHKO, INODETAULU * LOHKO);

    printf("tarkistus ja korjaus:\n");
    printf("  %d virhettä\n", pfs_tarkista(&l, true));
    printf("uusi tarkistus: %d virhettä\n", pfs_tarkista(&l, false));
    pfs_sulje(&l);
    // @loppu kaatuminen
    return 0;
}
