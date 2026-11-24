// Shakkilautalattia kahdella kolmiolla: affiininen vai
// perspektiivikorjattu interpolointi?
#include <cmath>
#include <cstdio>

#include "yhteinen/putki.hpp"

const int L = 96, K = 48;

// @alku varjostimet
Kohde piirra_lattia(bool korjaus) {
    Mat4 mvp = perspektiivi(1.2, double(L) / K, 0.5, 20) *
               katse({0, 1, 3}, {0, 0.2, -2}, {0, 1, 0}) *
               siirto(0, 0, -3);
    Malli lattia = taso(5, 10);  // kaksi kolmiota, 10 x 10 ruutua
    Kohde kohde(L, K, {0.02, 0.02, 0.05});
    auto verteksi = [&](const Verteksi& v) {
        return Tulos<2>{mvp * piste4(v.paikka), {v.uv.x, v.uv.y}};
    };
    auto fragmentti = [](const std::array<double, 2>& uv, const auto&) {
        int ruutu = int(std::floor(uv[0])) + int(std::floor(uv[1]));
        return ruutu % 2 ? Vari{0.9, 0.9, 0.9} : Vari{0.1, 0.1, 0.4};
    };
    Asetukset as;
    as.perspektiivikorjaus = korjaus;
    piirra(kohde, lattia, verteksi, fragmentti, as);
    return kohde;
}
// @loppu varjostimet

int main() {
    // @alku vertailu
    Kuva affiini = piirra_lattia(false).kuvaksi();
    Kuva oikea = piirra_lattia(true).kuvaksi();
    int eroja = 0;
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) eroja += !(affiini(x, y) == oikea(x, y));
    tilasto("affiininen", affiini);
    tilasto("korjattu", oikea);
    std::printf("eri värin saa %d pikseliä %d:sta\n", eroja, L * K);
    std::printf("affiininen:\n");
    ascii(affiini, 2, 4);
    std::printf("korjattu:\n");
    ascii(oikea, 2, 4);
    // @loppu vertailu

    // Kuvitusta varten molemmat rinnakkain.
    Kuva rinnakkain(2 * L + 4, K, {255, 255, 255});
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            rinnakkain(x, y) = affiini(x, y);
            rinnakkain(L + 4 + x, y) = oikea(x, y);
        }
    tallenna_ppm(rinnakkain, "06-perspektiivi.ppm");
}
