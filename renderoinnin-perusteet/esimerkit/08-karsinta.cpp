// Takapintojen karsinta: sama kuva, vähemmän työtä.
#include <cstdio>

#include "yhteinen/putki.hpp"

int main() {
    // @alku karsinta
    const int L = 64, K = 48;
    Mat4 mvp = perspektiivi(1.5, double(L) / K, 0.5, 20) *
               katse({2.4, 2, 3.2}, {0, 0, 0}, {0, 1, 0}) *
               kierto_y(0.6, 0.8);
    Malli m = kuutio();
    auto vv = [&](const Verteksi& v) {
        // Sivun väri normaalista: jokainen sivu omalla sävyllään.
        Vec3 n = v.normaali;
        return Tulos<3>{mvp * piste4(v.paikka),
                        {0.2 + 0.4 * (n.x + 1), 0.2 + 0.4 * (n.y + 1),
                         0.2 + 0.4 * (n.z + 1)}};
    };
    auto fv = [](const std::array<double, 3>& c, const auto&) {
        return Vari{c[0], c[1], c[2]};
    };
    std::printf("kolmiot karsitut fragmentit syv.hylätyt  summa     "
                "karsinta\n");
    for (bool karsinta : {false, true}) {
        Kohde kohde(L, K);
        Asetukset as;
        as.karsinta = karsinta;
        piirra(kohde, m, vv, fv, as);
        const Tilasto& t = kohde.tilasto;
        std::printf("%7ld %8ld %10ld %11ld  %08x  %s\n", t.kolmiot,
                    t.karsitut, t.fragmentit, t.syvyys_hylatyt,
                    tarkistussumma(kohde.kuvaksi()),
                    karsinta ? "päällä" : "pois");
    }
    // @loppu karsinta
}
