// Syvyyspuskuri: arvojen jakautuminen, leikkaavat kolmiot ja
// z-taistelu eri tarkkuuksilla.
#include <cmath>
#include <cstdio>
#include <string>

#include "yhteinen/putki.hpp"

int main() {
    // @alku jakauma
    // Syvyys d = (z_ndc + 1) / 2 etäisyyden funktiona.
    const double lahi = 0.1, kauka = 100;
    Mat4 p = perspektiivi(1, 1, lahi, kauka);
    std::printf("etäisyys     1/w   syvyys d   d:n porras 24 b  16 b\n");
    for (double e : {0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0}) {
        Vec4 c = p * piste4({0, 0, -e});
        double d = (c.z / c.w + 1) / 2;
        // d = A - B / e, joten dd/de = B / e^2 ja yksi syvyysporras
        // vastaa etäisyyttä e^2 / (B * 2^bitit).
        double B = kauka * lahi / (kauka - lahi);
        std::printf("%8.1f  %6.2f  %9.6f  %13.1e  %6.1e\n", e, 1 / e, d,
                    e * e / (B * std::ldexp(1.0, 24)),
                    e * e / (B * std::ldexp(1.0, 16)));
    }
    // @loppu jakauma

    // @alku piirto
    // Kaksi lattiaa 0.001 yksikön päässä toisistaan, etäisyydet 1..60.
    // Alempi (punainen) piirretään ensin, ylempi (sininen) sen päälle.
    const int L = 64, K = 32;
    Mat4 vp = perspektiivi(1.5, double(L) / K, lahi, kauka) *
              katse({0, 0, 0}, {0, -0.25, -1}, {0, 1, 0});
    auto lattia = [](double y) {
        Malli m;
        Vec3 n{0, 1, 0};
        m.nelikulmio({{-30, y, -1}, n, {}}, {{30, y, -1}, n, {}},
                     {{30, y, -60}, n, {}}, {{-30, y, -60}, n, {}});
        return m;
    };
    auto vv = [&](const Verteksi& v) {
        return Tulos<0>{vp * piste4(v.paikka), {}};
    };
    std::printf("\nsyvyysbitit  punaisia pikseleitä (pitäisi olla 0)\n");
    for (int bitit : {16, 24, 0}) {
        Kohde kohde(L, K);
        Asetukset as;
        as.syvyysbitit = bitit;
        piirra(kohde, lattia(-1), vv,
               [](const auto&, const auto&) { return Vari{1, 0, 0}; },
               as);
        piirra(kohde, lattia(-0.999), vv,
               [](const auto&, const auto&) { return Vari{0.1, 0.3, 1}; },
               as);
        Kuva kuva = kohde.kuvaksi();
        int punaisia = 0;
        for (Rgb c : kuva.pikselit()) punaisia += c.r > c.b;
        std::printf("%11s  %d / %d\n",
                    bitit ? std::to_string(bitit).c_str() : "double",
                    punaisia, L * K);
        for (int y = 10; bitit == 16 && y < 16; ++y) {  // kaukaiset rivit
            std::string rivi;
            for (int x = 0; x < L; ++x) {
                Rgb c = kuva(x, y);
                rivi += c.r > c.b ? '#' : c.b > 0 ? '.' : ' ';
            }
            std::printf("  |%s|\n", rivi.c_str());
        }
    }
    // @loppu piirto

#ifdef KUVITUS  // make kuvat: sama kohtaus suurempana, 16 ja 24 bittiä
    const int S = 4;
    Kuva rinnakkain(2 * L * S + 4, K * S, {90, 90, 90});
    int i = 0;
    for (int bitit : {16, 24}) {
        Kohde kohde(L * S, K * S, {0.02, 0.03, 0.06});
        Asetukset as;
        as.syvyysbitit = bitit;
        piirra(kohde, lattia(-1), vv,
               [](const auto&, const auto&) { return Vari{1, 0, 0}; },
               as);
        piirra(kohde, lattia(-0.999), vv,
               [](const auto&, const auto&) { return Vari{0.1, 0.3, 1}; },
               as);
        Kuva kuva = kohde.kuvaksi();
        for (int y = 0; y < K * S; ++y)
            for (int x = 0; x < L * S; ++x)
                rinnakkain(i * (L * S + 4) + x, y) = kuva(x, y);
        ++i;
    }
    tallenna_ppm(rinnakkain, "08-syvyys.ppm");
#endif
}
