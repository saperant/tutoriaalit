#ifndef KOMENTO_H
#define KOMENTO_H

// Komentorivityökalun alikomento. Jokainen alikomento rekisteröityy
// omassa tiedostossaan; keskitettyä luetteloa ei tarvita.
struct komento {
    const char *nimi;
    int (*aja)(void);
};

// @alku makro
// Sijoittaa kuvaajan osioon "komennot". Linkkeri kokoaa kaikkien
// tiedostojen kuvaajat peräkkäin ja määrittelee osion rajasymbolit
// __start_komennot ja __stop_komennot, koska osion nimi on kelvollinen
// C-tunniste. used estää kääntäjää poistamasta muuttujaa, ja
// tasaus pitää kuvaajat taulukkona ilman täytettä.
#define KOMENTO(n, f)                                                   \
    static const struct komento kuvaaja_##f                             \
        __attribute__((used, section("komennot"),                       \
                       aligned(_Alignof(struct komento)))) = {n, f}
// @loppu makro

#endif
