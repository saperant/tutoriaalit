// Lähdekoodin sijainnit ja virheilmoitukset.
#pragma once

#include <iostream>
#include <string>
#include <utility>

namespace kide {

// @alku sijainti
struct Sijainti {
    int rivi = 1;
    int sarake = 1;
};
// @loppu sijainti

// @alku diagnostiikka
// Kirjoittaa virheet muodossa tiedosto:rivi:sarake: virhe: viesti,
// jota editorit ja kehitysympäristöt osaavat lukea.
class Diagnostiikka {
public:
    explicit Diagnostiikka(std::string tiedosto)
        : tiedosto_(std::move(tiedosto)) {}

    void virhe(Sijainti s, const std::string& viesti) {
        ++virheita_;
        if (virheita_ <= kEnintaan) {
            std::cerr << tiedosto_ << ':' << s.rivi << ':' << s.sarake
                      << ": virhe: " << viesti << '\n';
        }
    }
    int virheita() const { return virheita_; }

private:
    static constexpr int kEnintaan = 20;  // loput vain lasketaan
    std::string tiedosto_;
    int virheita_ = 0;
};
// @loppu diagnostiikka

}  // namespace kide
