// Monitärkeysnäytteistys (MIS): kaksi strategiaa ja tasapainoheuristiikka.
#include <cmath>
#include <cstdio>

#include "yhteinen/kuva.hpp"
#include "yhteinen/naytteet.hpp"
#include "yhteinen/satunnainen.hpp"

// @alku tilanne
// Integraali F = int L(w) b(w) d omega: valo L0 kartiossa normaalin
// ympärillä (cos theta > cmax) ja kiiltolohko b = (k + 1) / 2pi cos^k.
// L0 valitaan niin, että tarkka arvo on F = 1.
struct Tilanne {
    const char* nimi;
    double k, cmax;
    double L0() const { return 1 / (1 - std::pow(cmax, k + 1)); }
    double lohko(double c) const {
        return (k + 1) / (2 * PII) * std::pow(c, k);
    }
    double valo_pdf() const { return 1 / (2 * PII * (1 - cmax)); }
};
// @loppu tilanne

// @alku strategiat
// Yksi estimaatti: n_l näytettä lohkosta ja n_v valosta. Kun
// kumpaakin käytetään, painot ovat tasapainoheuristiikka
// w_i = n_i p_i / (n_l p_l + n_v p_v).
double estimaatti(const Tilanne& T, int n_l, int n_v, Pcg32& g) {
    double s = 0;
    auto paino = [&](double c, double p) {   // p = valitun strategian pdf
        double pl = T.lohko(c), pv = c > T.cmax ? T.valo_pdf() : 0;
        return p / (n_l * pl + n_v * pv);    // = w_i / (n_i p_i) * p_i
    };
    for (int i = 0; i < n_l; ++i) {           // lohkon näytteet
        double c = std::pow(g.tasainen(), 1 / (T.k + 1));
        if (c > T.cmax)
            s += T.L0() * T.lohko(c) * paino(c, 1);
    }
    for (int i = 0; i < n_v; ++i) {           // valon näytteet
        double u1 = g.tasainen(), u2 = g.tasainen();
        double c = kartio(u1, u2, T.cmax).z;
        s += T.L0() * T.lohko(c) * paino(c, 1);
    }
    return s;
}
// @loppu strategiat

int main() {
    // @alku main
    const Tilanne tilanteet[] = {{"pieni valo, laaja lohko", 1, 0.9999},
                                 {"suuri valo, terävä lohko", 2000, 0.5}};
    std::printf("RMSE, 16 näytettä, tarkka arvo 1\n");
    std::printf("tilanne                      lohko     valo      MIS\n");
    for (const Tilanne& T : tilanteet) {
        otsake(T.nimi, 26);
        for (auto [n_l, n_v] : {std::pair{16, 0}, {0, 16}, {8, 8}}) {
            double v = 0;
            for (int r = 0; r < 400; ++r) {
                Pcg32 g(static_cast<std::uint64_t>(r), n_l);
                double e = estimaatti(T, n_l, n_v, g);
                v += (e - 1) * (e - 1) / 400;
            }
            std::printf("  %7.4f", std::sqrt(v));
        }
        std::printf("\n");
    }
    // @loppu main
}
