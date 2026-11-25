// Determinismi: sama syöte tuottaa saman tilan bitilleen, ja mikä sen
// rikkoo. Argumentilla "tiiviste" tulostetaan myös itse tiiviste, jota
// voi verrata eri kääntäjien ja koneiden välillä.
#include "yhteinen/maailma.hpp"
#include "yhteinen/tulostus.hpp"

#include <cstdint>
#include <cstring>
#include <print>
#include <string_view>

// @alku tiiviste
// FNV-1a kappaleiden tilan tavuista: yhdenkin bitin ero muuttaa tuloksen.
std::uint64_t tiiviste(const Maailma& m) {
    std::uint64_t h = 1469598103934665603ull;
    auto lisaa = [&h](double x) {
        unsigned char tavut[sizeof x];
        std::memcpy(tavut, &x, sizeof x);
        for (unsigned char t : tavut) h = (h ^ t) * 1099511628211ull;
    };
    for (const Kappale& k : m.kappaleet)
        for (double x : {k.sijainti.x, k.sijainti.y, k.sijainti.z,
                         k.kierto.w, k.kierto.x, k.kierto.y, k.kierto.z,
                         k.nopeus.x, k.nopeus.y, k.nopeus.z,
                         k.kulmanopeus.x, k.kulmanopeus.y, k.kulmanopeus.z})
            lisaa(x);
    return h;
}
// @loppu tiiviste

// @alku kohtaus
// Laatikkopino ja siihen osuva pallo. Laatikot lisätään annetussa
// järjestyksessä; pallo on aina viimeinen.
Maailma kohtaus(bool kaanteinen_jarjestys = false) {
    Maailma m;
    m.lisaa(tee_taso());
    for (int n = 0; n < 6; ++n) {
        int i = kaanteinen_jarjestys ? 5 - n : n;
        m.lisaa(tee_laatikko(1.0, {0.4, 0.25, 0.4},
                             {0.1 * (i % 2), 0.25 + 0.5 * i, 0}));
    }
    Kappale pallo = tee_pallo(3.0, 0.3, {0.2, 1.2, 5});
    pallo.nopeus = {0, 1, -9};
    m.lisaa(pallo);
    return m;
}
void aja(Maailma& m, int askelia) {
    for (int i = 0; i < askelia; ++i) m.askel();
}
// Pallon (viimeinen kappale) etäisyys toisen ajon pallosta.
double ero(const Maailma& a, const Maailma& b) {
    return pituus(a.kappaleet.back().sijainti - b.kappaleet.back().sijainti);
}
// @loppu kohtaus

int main(int argc, char** argv) {
    auto sama = [](const Maailma& a, const Maailma& b) {
        return tiiviste(a) == tiiviste(b) ? "sama" : "ERI";
    };
    // @alku toisto
    Maailma vertailu = kohtaus();
    aja(vertailu, 300);
    Maailma toinen = kohtaus();
    aja(toinen, 300);
    std::println("sama ajo kahdesti:               {}",
                 sama(vertailu, toinen));
    // @loppu toisto

    // @alku vedos
    // Tilannevedos kesken ajon: koko maailman kopio.
    Maailma alku = kohtaus();
    aja(alku, 100);
    Maailma vedos = alku;  // sisältää myös ratkaisijan muistin
    aja(vedos, 200);
    std::println("jatko tilannevedoksesta:         {}",
                 sama(vertailu, vedos));
    // Sama vedos ilman kosketusten kertyneitä impulsseja.
    Maailma vajaa = alku;
    vajaa.monistot.clear();
    aja(vajaa, 200);
    std::println("vedos ilman ratkaisijan muistia: {}  (pallo {} m sivussa)",
                 sama(vertailu, vajaa), luku(ero(vertailu, vajaa), 3));
    // @loppu vedos

    // @alku jarjestys
    // Samat kappaleet eri järjestyksessä: rajoitteet ratkaistaan eri
    // järjestyksessä, ja pyöristysvirheet kertyvät eri tavalla.
    Maailma kaannetty = kohtaus(true);
    aja(kaannetty, 300);
    std::println("kappaleet eri järjestyksessä:    pallo {} m sivussa",
                 luku(ero(vertailu, kaannetty), 3));
    // @loppu jarjestys

    // @alku askel
    // Sama viisi sekuntia eri aika-askelella, kuten kävisi, jos askel
    // seuraisi ruudunpäivitystä.
    for (int taajuus : {50, 75, 144}) {
        Maailma m = kohtaus();
        m.asetukset.dt = 1.0 / taajuus;
        aja(m, 5 * taajuus);
        std::println("askel 1/{:<3} s:                   pallo {} m sivussa",
                     taajuus, luku(ero(vertailu, m), 3));
    }
    // @loppu askel

    if (argc > 1 && std::string_view(argv[1]) == "tiiviste")
        std::println("tiiviste {:016x}", tiiviste(vertailu));
}
