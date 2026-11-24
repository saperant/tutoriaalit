// Polun katkaisu: kiinteä syvyys on harhainen, venäläinen ruletti ei.
#include <cstdio>

#include "yhteinen/cornell.hpp"
#include "yhteinen/polku.hpp"

const int L = 40, K = 30;

int main() {
    // @alku main
    Kohtaus K_ = cornell({}, {.vari = {0.2, 0.3, 0.75}});
    Kamera k = cornell_kamera(L, K);
    std::printf("pomput  ruletti  keskiarvo  säteitä/polku\n");
    for (auto [pomput, ruletti] : {std::pair{1, false}, {2, false},
                                   {3, false}, {5, false}, {50, false},
                                   {50, true}}) {
        Laskuri l;
        Asetukset a{.pomput = pomput, .ruletti = ruletti,
                    .nayta_valot = false};
        Kehys kuva = renderoi(K_, k, 16, 4, a, l);
        std::printf("%6d  %7s  %9.4f  %13.2f\n", pomput,
                    ruletti ? "on" : "ei", keskiarvo(kuva),
                    static_cast<double>(l.sateet) / l.polut);
    }
    // @loppu main
}
