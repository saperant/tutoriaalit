// Sävykuvaus: suuren dynamiikan radianssi näytön tavuiksi.
#include <cstdio>
#include <initializer_list>

#include "yhteinen/kuva.hpp"
#ifdef KUVITUS  // make kuvat: Cornellin laatikko kolmella käyrällä
#include "yhteinen/cornell.hpp"
#include "yhteinen/polku.hpp"
#endif

// @alku kayrat
// Kaikki käyrät kuvaavat radianssin x >= 0 välille [0, 1], minkä
// jälkeen tulee sRGB-koodaus.
double leikkaus(double x) { return std::min(x, 1.0); }
double reinhard(double x) { return x / (1 + x); }
// Laajennettu Reinhard: valkoinen piste W kuvautuu arvoon 1.
double reinhard_w(double x, double W) {
    return x * (1 + x / (W * W)) / (1 + x);
}
// ACES-elokuvakäyrän sovite (Narkowicz 2015).
double aces(double x) {
    return std::clamp(x * (2.51 * x + 0.03) / (x * (2.43 * x + 0.59) + 0.14),
                      0.0, 1.0);
}
// @loppu kayrat

int main() {
    // @alku taulukko
    std::printf("radianssi  leikkaus  Reinhard  Reinhard W=8  ACES\n");
    for (double x : {0.01, 0.05, 0.18, 0.5, 1.0, 2.0, 4.0, 8.0, 32.0}) {
        std::printf("%9.2f  %8d  %8d  %12d  %4d\n", x,
                    srgb_tavu(leikkaus(x)), srgb_tavu(reinhard(x)),
                    srgb_tavu(reinhard_w(x, 8)), srgb_tavu(aces(x)));
    }
    // @loppu taulukko

#ifdef KUVITUS
    // Sama renderöity kehys ylivalotettuna (valotus 4), jotta katto ja
    // valon ympäristö ylittävät näytön valkoisen.
    const int L = 160, K = 120;
    Kohtaus kohtaus = cornell({}, {.vari = {0.2, 0.3, 0.75}});
    Laskuri l;
    Kehys kehys = renderoi(kohtaus, cornell_kamera(L, K), 256, 3, {}, l);
    Kehys rinnakkain(3 * L + 8, K);
    double (*kayrat[])(double) = {leikkaus, reinhard, aces};
    for (int i = 0; i < 3; ++i)
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x) {
                Vari v = 4.0 * kehys(x, y);
                rinnakkain(i * (L + 4) + x, y) = {kayrat[i](v.r),
                                                  kayrat[i](v.g),
                                                  kayrat[i](v.b)};
            }
    tallenna_ppm(rinnakkain, "10-savykuvaus.ppm");
#endif
}
