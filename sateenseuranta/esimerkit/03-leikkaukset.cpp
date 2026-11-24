// Leikkausfunktioiden testit: tunnetut tapaukset ja satunnaistesti.
#include <cstdio>

#include "yhteinen/kuva.hpp"
#include "yhteinen/satunnainen.hpp"
#include "yhteinen/sade.hpp"

void rivi(const char* nimi, double t) {
    otsake(nimi, 24);
    if (t == AARETON)
        std::printf("ohi\n");
    else
        std::printf("t = %.6f\n", t);
}

int main() {
    // @alku tunnetut
    Sade z{{0, 0, -5}, {0, 0, 1}};          // kohti origoa pitkin z:aa
    Pallo yksikko{{0, 0, 0}, 1};
    rivi("pallo edestä", leikkaa_pallo(yksikko, z, 0, AARETON));
    rivi("pallo sisältä", leikkaa_pallo(yksikko, {{0, 0, 0}, {0, 0, 1}},
                                        0, AARETON));
    rivi("pallo, tmax = 3", leikkaa_pallo(yksikko, z, 0, 3));
    rivi("pallo sivuun", leikkaa_pallo(yksikko, {{0, 1.5, -5}, {0, 0, 1}},
                                       0, AARETON));
    rivi("taso z = 2", leikkaa_taso({{0, 0, 1}, 2}, z, 0, AARETON));
    rivi("taso takana", leikkaa_taso({{0, 0, 1}, -6}, z, 0, AARETON));
    Kolmio k{{-1, -1, 0}, {1, -1, 0}, {0, 1, 0}};
    rivi("kolmio keskeltä", leikkaa_kolmio(k, z, 0, AARETON).t);
    rivi("kolmio kärjen ohi",
         leikkaa_kolmio(k, {{0.9, 0.9, -5}, {0, 0, 1}}, 0, AARETON).t);
    Laatikko b{{-1, -1, -1}, {1, 1, 1}};
    rivi("laatikko edestä", leikkaa_laatikko(b, z, kaanteinen(z.d), 0,
                                             AARETON));
    rivi("laatikko, reunan taso",
         leikkaa_laatikko(b, {{1, 0, -5}, {0, 0, 1}}, kaanteinen(z.d), 0,
                          AARETON));
    rivi("laatikko sisältä",
         leikkaa_laatikko(b, {{0, 0, 0}, {0, 0, 1}}, kaanteinen(z.d), 0,
                          AARETON));
    // @loppu tunnetut

    // @alku satunnainen
    // Möller–Trumbore vertailuversiota vastaan: tason leikkaus ja
    // pinta-alasuhteista lasketut barysentriset painot. Kiinteä
    // siemen tekee testistä toistettavan.
    Pcg32 g(42);
    auto r = [&g] { return 4 * g.tasainen() - 2; };
    int osumia = 0, eroja = 0, rajalla = 0;
    for (int i = 0; i < 100000; ++i) {
        Kolmio tk{{r(), r(), r()}, {r(), r(), r()}, {r(), r(), r()}};
        Sade s{{r(), r(), r() - 6}, normalisoi({r(), r(), 4})};
        double t1 = leikkaa_kolmio(tk, s, 0, AARETON).t;
        Vec3 n = risti(tk.b - tk.a, tk.c - tk.a);
        double t2 = AARETON, reuna = 1;
        double t = leikkaa_taso({normalisoi(n), piste(normalisoi(n), tk.a)},
                                s, 0, AARETON);
        if (t < AARETON) {
            Vec3 p = kohta(s, t);
            double wa = piste(risti(tk.b - p, tk.c - p), n) / piste(n, n);
            double wb = piste(risti(tk.c - p, tk.a - p), n) / piste(n, n);
            double wc = 1 - wa - wb;
            reuna = std::min({std::fabs(wa), std::fabs(wb), std::fabs(wc)});
            if (wa >= 0 && wb >= 0 && wc >= 0) t2 = t;
        }
        osumia += t1 < AARETON;
        if ((t1 < AARETON) != (t2 < AARETON)) {
            if (reuna < 1e-9) ++rajalla; else ++eroja;
        } else if (t1 < AARETON && std::fabs(t1 - t2) > 1e-9 * t2) {
            ++eroja;
        }
    }
    std::printf("satunnaistesti: %d osumaa, %d eroa, %d reunalla\n",
                osumia, eroja, rajalla);
    // @loppu satunnainen
}
