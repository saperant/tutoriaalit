// tuote.hpp: tuoterekisterin tyyppi ja vertailufunktiot.
#ifndef TUOTE_HPP
#define TUOTE_HPP

struct Tuote {
    int tunnus;
    int hinta_snt;
};

// @alku vertailut
// Määritelty otsakkeessa: jokainen käännösyksikkö näkee rungon, joten
// kääntäjä voi sisällyttää sen. inline sallii saman määritelmän
// useassa käännösyksikössä (ODR, one definition rule).
inline bool hinta_ensin(const Tuote& a, const Tuote& b)
{
    return a.hinta_snt < b.hinta_snt;
}

// Vain esittely: runko on tiedostossa tuote.cpp.
bool hinta_ensin_erillinen(const Tuote& a, const Tuote& b);
// @loppu vertailut

#endif
