// Kaukaisuuteen jatkuva tekstuuroitu taso kolmella suodattimella.
// Vertailukuva lasketaan 4 x 4 -ylinäytteistyksellä.
#include <cmath>
#include <cstdio>
#include <cstdlib>

#include "yhteinen/putki.hpp"
#include "yhteinen/tekstuuri.hpp"

const int L = 96, K = 48;
const Mipmap MIP(shakki(64, 4, {0.9, 0.9, 0.9}, {0.05, 0.1, 0.3}));

// @alku piirto
enum class Suodin { lahin, bilineaarinen, trilineaarinen };

Kohde piirra_taso(Suodin s, int n) {  // n = ylinäytteistyskerroin
    Mat4 mvp = perspektiivi(1.2, double(L) / K, 0.5, 100) *
               katse({0, 1, 4}, {0, 0.3, -2}, {0, 1, 0});
    Malli m = taso(30, 4);  // tekstuuri toistuu 4 x 4 kertaa
    Kohde kohde(L * n, K * n, {0.5, 0.6, 0.8});
    auto vv = [&](const Verteksi& v) {
        return Tulos<2>{mvp * piste4(v.paikka), {v.uv.x, v.uv.y}};
    };
    auto fv = [&](const std::array<double, 2>& uv, const auto& f) {
        Vec2 p{uv[0], uv[1]};
        if (s == Suodin::lahin) return MIP.tasot[0].lahin(p);
        if (s == Suodin::bilineaarinen)
            return MIP.tasot[0].bilineaarinen(p);
        double lod = MIP.taso({f.ddx[0], f.ddx[1]}, {f.ddy[0], f.ddy[1]});
        return MIP.trilineaarinen(p, lod);
    };
    Asetukset as;
    as.derivaatat = true;
    piirra(kohde, m, vv, fv, as);
    return kohde;
}
// @loppu piirto

int main() {
    // @alku vertailu
    Kuva vertailu = piirra_taso(Suodin::bilineaarinen, 4).pienennetty(4);
    tilasto("vertailu", vertailu);
    const char* nimet[] = {"lähin", "bilineaarinen", "trilineaarinen"};
    Kuva kaikki(L, 4 * K + 6, {255, 255, 255});
    for (int i = 0; i < 3; ++i) {
        Kuva kuva = piirra_taso(static_cast<Suodin>(i), 1).kuvaksi();
        // Keskimääräinen kirkkausero vertailuun ylä- ja alapuoliskossa.
        long kauka = 0, lahi = 0;
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x) {
                int e = std::abs(kirkkaus(kuva(x, y)) -
                                 kirkkaus(vertailu(x, y)));
                (y < K / 2 ? kauka : lahi) += e;
                kaikki(x, i * (K + 2) + y) = kuva(x, y);
            }
        tilasto(nimet[i], kuva);
        std::printf("%15svirhe yläpuolella %.1f, alapuolella %.1f\n", "",
                    double(kauka) / (L * K / 2),
                    double(lahi) / (L * K / 2));
    }
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x)
            kaikki(x, 3 * (K + 2) + y) = vertailu(x, y);
    tallenna_ppm(kaikki, "10-mipmap.ppm");
    // @loppu vertailu
}
