// Lattia jatkuu kameran taakse: ilman lähitason leikkausta kolmio
// projisoituu väärin.
#include <cmath>
#include <cstdio>

#include "yhteinen/putki.hpp"

const int L = 64, K = 32;

// Pyöristys kolmeen desimaaliin ilman tulostetta -0.000.
double r3(double v) { return std::round(v * 1000) / 1000 + 0.0; }

void nayta(const char* nimi, Vec4 c) {
    std::printf("  %-4s x %7.3f  y %7.3f  z %7.3f  w %7.3f  z+w %7.3f\n",
                nimi, r3(c.x), r3(c.y), r3(c.z), r3(c.w), r3(c.z + c.w));
}

int main() {
    // @alku kolmio
    Mat4 vp = perspektiivi(1.2, double(L) / K, 0.5, 20) *
              katse({0, 1, 0}, {0, 0.6, -4}, {0, 1, 0});
    // Lattiakolmio, jonka yksi kärki on kameran takana.
    std::vector<Tulos<0>> kolmio = {{vp * piste4({3, 0, -6}), {}},
                                    {vp * piste4({-3, 0, -6}), {}},
                                    {vp * piste4({0, 0, 4}), {}}};
    std::printf("leikkausavaruudessa:\n");
    const char* nimet[] = {"a", "b", "c", "d"};
    for (std::size_t i = 0; i < 3; ++i) nayta(nimet[i], kolmio[i].paikka);
    std::vector<Tulos<0>> leikattu = leikkaa_lahitaso(kolmio);
    std::printf("leikattuna %zu kärkeä:\n", leikattu.size());
    for (std::size_t i = 0; i < leikattu.size(); ++i)
        nayta(nimet[i], leikattu[i].paikka);
    // @loppu kolmio

    // @alku vertailu
    Malli m;
    m.verteksit = {{{3, 0, -6}, {}, {}}, {{-3, 0, -6}, {}, {}},
                   {{0, 0, 4}, {}, {}}};
    m.kolmiot = {{0, 1, 2}};
    for (bool leikkaa : {true, false}) {
        Kohde kohde(L, K);
        Asetukset as;
        as.leikkaa = leikkaa;
        as.karsinta = false;  // peilautunut kolmio on väärin päin
        piirra(kohde, m,
               [&](const Verteksi& v) {
                   return Tulos<0>{vp * piste4(v.paikka), {}};
               },
               [](const auto&, const auto&) { return Vari{1, 1, 1}; },
               as);
        Kuva kuva = kohde.kuvaksi();
        std::printf("\nleikkaus %s, leikattuja kolmioita %ld\n",
                    leikkaa ? "päällä" : "pois", kohde.tilasto.leikatut);
        tilasto("lattia", kuva);
        ascii(kuva, 1, 2);
    }
    // @loppu vertailu
}
