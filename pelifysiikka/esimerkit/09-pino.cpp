// Simulaatioaskel kokonaisuutena: pyramidi asettuu lepoon, nukahtaa ja
// herää, kun pallo osuu siihen. Argumenttina annettuun nimeen
// tallennetaan kuvasarja.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku pyramidi
// Kymmenen laatikon pyramidi ja sitä kohti myöhemmin heitettävä pallo.
Maailma pyramidi() {
    Maailma m;
    m.asetukset.nukahtaminen = true;
    m.lisaa(tee_taso());
    for (int rivi = 0; rivi < 4; ++rivi)
        for (int i = 0; i < 4 - rivi; ++i)
            m.lisaa(tee_laatikko(
                1.0, {0.5, 0.25, 0.4},
                {-1.65 + 0.55 * rivi + 1.1 * i, 0.25 + 0.5 * rivi, 0}));
    return m;
}
// @loppu pyramidi

int main(int argc, char** argv) {
    Maailma m = pyramidi();
    Kamera kamera{{4.5, 2.6, 7.5}, {0, 1.0, 0}, 40, 1.5};
    int kuvia = 0;

    // @alku ajo
    std::println("{:>6} {:>6} {:>9} {:>8} {:>9} {:>10}", "aika", "parit",
                 "monistot", "pisteet", "hereillä", "energia");
    double suurin_kasvu = 0, edellinen = energia(m);
    for (int askel = 0; askel <= 360; ++askel) {
        if (askel == 180) {  // kolmen sekunnin kohdalla heitetään pallo
            Kappale pallo = tee_pallo(4.0, 0.35, {0.3, 1.0, 6});
            pallo.nopeus = {0, 1.5, -14};
            m.lisaa(pallo);
            edellinen = energia(m);
        }
        if (askel % 30 == 0)
            std::println("{:>6} {:>6} {:>9} {:>8} {:>9} {:>8} J",
                         luku(askel / 60.0, 1), m.tilasto.parit,
                         m.tilasto.monistot, m.tilasto.pisteet,
                         m.tilasto.hereilla, luku(energia(m), 1));
        if (argc > 1 && (askel == 170 || askel == 200 || askel == 215 ||
                         askel == 240 || askel == 290 || askel == 360))
            tallenna_kuva(m, kamera, argv[1], ++kuvia, 300);
        m.askel();
        // Törmäykset ja kitka saavat hävittää energiaa, mutta mikään
        // ei saa tuottaa sitä.
        suurin_kasvu = std::max(suurin_kasvu, energia(m) - edellinen);
        edellinen = energia(m);
    }
    std::println("suurin energian kasvu yhdessä askeleessa: {} J",
                 luku(suurin_kasvu, 3));
    // @loppu ajo

    // @alku lepo
    int levossa = 0;
    double korkein = 0;
    for (const Kappale& k : m.kappaleet) {
        if (!k.liikkuva()) continue;
        if (k.unessa) ++levossa;
        korkein = std::max(korkein, k.sijainti.y);
    }
    std::println("\nlopussa unessa {} / {}, korkein kappale {} m", levossa,
                 m.kappaleet.size() - 1, luku(korkein));
    int n = static_cast<int>(m.kappaleet.size());
    std::println("kaikki parit {}, laajan vaiheen jälkeen {}",
                 n * (n - 1) / 2, m.tilasto.parit);
    // @loppu lepo
}
