// Koko putki: tekstuuroitu lattia, kuutio ja valaistu pallo.
#include <cstdio>

#include "varjostin.hpp"

#ifdef KUVITUS  // make kuvat: sama kohtaus suurempana kirjan kuvaksi
const int L = 480, K = 320, N = 2;
#else
const int L = 120, K = 80, N = 2;  // kuvan koko ja ylinäytteistys
#endif

// @alku kohtaus
struct Kappale {
    const char* nimi;
    Malli malli;
    Mat4 muunnos;
    Materiaali aine;
    const Mipmap* tekstuuri;
};

int main() {
    const Mipmap lattiakuvio(shakki(64, 8, {0.8, 0.8, 0.8},
                                    {0.25, 0.25, 0.3}));
    const Mipmap laatat(shakki(32, 8, {1, 0.9, 0.6}, {0.9, 0.4, 0.2}));
    const Materiaali matta{{0.03, 0.03, 0.04}, {1, 1, 1}, {0, 0, 0}, 1};
    const Materiaali kiiltava{{0.02, 0.03, 0.05}, {0.1, 0.35, 0.8},
                              {0.7, 0.7, 0.7}, 60};
    const Kappale kappaleet[] = {
        {"lattia", taso(6, 3), yksikko(), matta, &lattiakuvio},
        {"kuutio", kuutio(),
         siirto(-1, 0.8, 0) * kierto_y(0.6, 0.8) *
             skaalaus(0.8, 0.8, 0.8),
         matta, &laatat},
        {"pallo", pallo(3), siirto(1.4, 0.9, 0.6) *
                                skaalaus(0.9, 0.9, 0.9),
         kiiltava, nullptr},
    };
    Yhteiset u;
    u.silma = {1.5, 3, 6};
    u.vp = perspektiivi(1.6, double(L) / K, 0.5, 50) *
           katse(u.silma, {0, 0.5, 0}, {0, 1, 0});
    u.valo = normalisoi({0.3, 1, 0.6});
    u.valon_vari = {1, 0.95, 0.9};
    // @loppu kohtaus

    // @alku piirtokutsut
    Kohde kohde(L * N, K * N, {0.45, 0.55, 0.75});
    Asetukset as;
    as.derivaatat = true;  // mipmap-tason valintaa varten
    std::printf("kappale  kolmiot karsitut leikatut fragmentit "
                "syv.hylätyt\n");
    for (const Kappale& k : kappaleet) {
        Tilasto ennen = kohde.tilasto;
        Varjostin v;
        v.u = u;
        v.u.malli = k.muunnos;
        v.aine = k.aine;
        v.tekstuuri = k.tekstuuri;
        piirra(kohde, k.malli, v, v, as);  // sama olio molemmille
        const Tilasto& t = kohde.tilasto;
        std::printf("%-7s  %7ld %8ld %8ld %10ld %11ld\n", k.nimi,
                    t.kolmiot - ennen.kolmiot, t.karsitut - ennen.karsitut,
                    t.leikatut - ennen.leikatut,
                    t.fragmentit - ennen.fragmentit,
                    t.syvyys_hylatyt - ennen.syvyys_hylatyt);
    }
    // @loppu piirtokutsut

    // @alku tulos
    Kuva kuva = kohde.pienennetty(N);
    tallenna_ppm(kuva, "12-putki.ppm");
    std::printf("fragmentteja pikseliä kohden %.2f\n",
                double(kohde.tilasto.fragmentit) / (L * N * K * N));
    tilasto("kohtaus", kuva, koodaa({0.45, 0.55, 0.75}));
    // @loppu tulos
}
