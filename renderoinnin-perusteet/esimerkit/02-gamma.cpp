// Lineaarinen valo, sRGB-koodaus ja kuva PPM-tiedostoksi.
#include <cstdio>
#include <fstream>

#include "yhteinen/kuva.hpp"

int main() {
    // @alku taulukko
    std::printf("lineaarinen  sRGB-tavu  naiivi tavu\n");
    for (double v : {0.0, 0.01, 0.05, 0.18, 0.5, 1.0}) {
        std::printf("%11.2f  %9d  %11d\n", v, tavuksi(srgb_koodaa(v)),
                    tavuksi(v));
    }
    std::printf("tavu 128 on lineaarisena %.3f\n", srgb_pura(128 / 255.0));
    // @loppu taulukko

    // @alku sekoitus
    // Punaisen ja vihreän keskiarvo kahdella tavalla.
    Rgb punainen{255, 0, 0}, vihrea{0, 255, 0};
    Rgb naiivi{128, 128, 0};
    Rgb oikea = koodaa(0.5 * pura(punainen) + 0.5 * pura(vihrea));
    std::printf("keskiarvo tavuista: (%d, %d, %d), kirkkaus %d\n",
                naiivi.r, naiivi.g, naiivi.b, kirkkaus(naiivi));
    std::printf("keskiarvo valosta:  (%d, %d, %d), kirkkaus %d\n",
                oikea.r, oikea.g, oikea.b, kirkkaus(oikea));
    // @loppu sekoitus

    // @alku liuku
    // Yläpuoli: tavu kasvaa tasaisesti. Alapuoli: valo kasvaa
    // tasaisesti. Keskellä shakkiruutu, jonka keskiarvo on puolet
    // valosta.
    Kuva kuva(64, 24);
    for (int x = 0; x < 64; ++x) {
        double t = x / 63.0;
        for (int y = 0; y < 8; ++y) {
            std::uint8_t a = tavuksi(t);
            kuva(x, y) = {a, a, a};
            std::uint8_t s = (x + y) % 2 ? 255 : 0;
            kuva(x, y + 8) = x < 32 ? Rgb{s, s, s} : koodaa({0.5, 0.5, 0.5});
            kuva(x, y + 16) = koodaa({t, t, t});
        }
    }
    tallenna_ppm(kuva, "02-gamma.ppm");
    std::ifstream f("02-gamma.ppm", std::ios::binary | std::ios::ate);
    std::printf("02-gamma.ppm: %ld tavua (otsikko 13 + 64 * 24 * 3)\n",
                static_cast<long>(f.tellg()));
    tilasto("liuku", kuva);
    // @loppu liuku
}
