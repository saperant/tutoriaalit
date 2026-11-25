// Ensimmäinen simulaatio: pallo vierii ramppia alas ja kaataa tornin.
// Argumenttina annettuun nimeen tallennetaan kuvasarja.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

int main(int argc, char** argv) {
    // @alku maailma
    Maailma m;
    m.lisaa(tee_taso());  // lattia
    // Ramppi: liikkumaton, kallistettu laatikko.
    m.lisaa(tee_seina({1.5, 0.1, 0.6}, {-2.6, 0.75, 0},
                      akselikulma({0, 0, 1}, rad(-25))));
    int pallo = m.lisaa(tee_pallo(5.0, 0.3, {-3.7, 1.75, 0}));
    // Torni: neljä laatikkoa päällekkäin.
    int alin = 0;
    for (int i = 0; i < 4; ++i) {
        int k = m.lisaa(tee_laatikko(1.0, {0.25, 0.3, 0.25},
                                     {1.5, 0.3 + 0.6 * i, 0}));
        if (i == 0) alin = k;
    }
    // @loppu maailma

    Kamera kamera{{0.5, 2.8, 7.5}, {-0.6, 0.9, 0}, 40, 2.0};
    int kuvia = 0;

    // @alku silmukka
    // Pelisilmukan fysiikkaosa: yksi kiinteän mittainen askel kerrallaan.
    for (int askel = 0; askel <= 240; ++askel) {
        if (askel % 40 == 0) {
            const Kappale& p = m.kappaleet[pallo];
            const Kappale& ylin = m.kappaleet[alin + 3];
            std::println("t = {} s: pallo {} vauhti {} m/s, "
                         "tornin huippu y = {}",
                         luku(askel / 60.0, 2), teksti(p.sijainti),
                         luku(pituus(p.nopeus)), luku(ylin.sijainti.y));
        }
        if (argc > 1 && (askel == 0 || askel == 70 || askel == 100 ||
                         askel == 120 || askel == 150 || askel == 240))
            tallenna_kuva(m, kamera, argv[1], ++kuvia, 360);
        m.askel();
    }
    // @loppu silmukka
}
