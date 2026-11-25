#ifndef VIESTI_H
#define VIESTI_H
#include <stddef.h>
#include <stdint.h>

// @alku huono
// Kenttien järjestys kirjoitusjärjestyksessä: tasaus lisää täytettä.
struct viesti_huono {
    uint8_t tyyppi;      // 1 tavu + 7 täytettä
    uint64_t aikaleima;  // tasattava 8:lla
    uint16_t pituus;     // 2 tavua + 2 täytettä
    uint32_t tarkiste;   // 4 tavua
};
// @loppu huono

// @alku hyva
// Sama tieto suurimmasta pienimpään järjestettynä.
struct viesti {
    uint64_t aikaleima;
    uint32_t tarkiste;
    uint16_t pituus;
    uint8_t tyyppi;
    uint8_t varattu;     // näkyvä täyte, käyttöön myöhemmin ABI:a rikkomatta
};

// Rajapinnan asettelu lukitaan käännösaikaisilla tarkistuksilla.
_Static_assert(sizeof(struct viesti) == 16, "viestin koko muuttui");
_Static_assert(offsetof(struct viesti, pituus) == 12, "pituus siirtyi");
// @loppu hyva

// @alku pakattu
// Levyllä tai verkossa kulkeva muoto ilman täytettä.
struct __attribute__((packed)) viesti_levy {
    uint8_t tyyppi;
    uint64_t aikaleima;
    uint16_t pituus;
    uint32_t tarkiste;
};
// @loppu pakattu
#endif
