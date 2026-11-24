// Linearisoituvuuden tarkistin käsin kirjoitetuilla historioilla.
#include <cstdio>
#include <vector>

#include "yhteinen/historia.hpp"

void tulosta(const char* nimi, const std::vector<Operaatio>& h) {
    Linearisoija l(h, 0);
    std::vector<std::size_t> j;
    bool ok = l.tarkista(j);
    std::printf("%-32s %s", nimi, ok ? "linearisoituva:" : "EI");
    for (std::size_t i : j) {
        const auto& o = l.operaatiot()[i];
        std::printf(" %c%d", o.kirjoitus ? 'w' : 'r', o.arvo);
    }
    std::printf("\n");
}

int main() {
    // @alku historiat
    // {asiakas, kirjoitus, arvo, alku, loppu}; rekisterin alkuarvo 0.
    tulosta("perakkain", {{0, true, 1, 0, 10}, {1, false, 1, 20, 30}});
    tulosta("lukuja kirjoituksen aikana",
            {{0, true, 1, 0, 30}, {1, false, 0, 5, 10},
             {2, false, 1, 15, 20}});
    tulosta("uusi ja sitten vanha",
            {{0, true, 1, 0, 50}, {1, false, 1, 10, 20},
             {2, false, 0, 30, 40}});
    tulosta("vanha luku kirjoituksen jalkeen",
            {{0, true, 1, 0, 10}, {1, false, 0, 20, 30}});
    tulosta("kesken jaanyt kirjoitus",
            {{0, true, 1, 0, KESKEN}, {1, false, 1, 100, 110},
             {1, false, 1, 120, 130}});
    tulosta("kaksi kirjoittajaa",
            {{0, true, 1, 0, 40}, {1, true, 2, 10, 30},
             {2, false, 2, 35, 45}, {2, false, 1, 50, 60}});
    // @loppu historiat
}
