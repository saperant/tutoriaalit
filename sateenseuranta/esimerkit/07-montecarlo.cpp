// Monte Carlo -integrointi: irradianssi taivaalta kolmella
// estimaattorilla ja virheen pieneneminen näytemäärän mukana.
#include <cmath>
#include <cstdio>

#include "yhteinen/naytteet.hpp"
#include "yhteinen/satunnainen.hpp"

// @alku taivas
// Taivaan radianssi on kirkkain lakipisteessä: L = 1 + 2 cos(theta).
// Irradianssi E = int L cos d omega = pi + 4 pi / 3 = 7 pi / 3.
double taivas(Vec3 w) { return 1 + 2 * w.z; }
const double TARKKA = 7 * PII / 3;
// @loppu taivas

// @alku estimaattorit
// Yksi estimaatti N näytteestä: keskiarvo arvoista f(w) / pdf(w).
enum class Tapa { tasainen, kosini, unohtunut_pdf };
double estimaatti(Tapa tapa, int N, Pcg32& g) {
    double s = 0;
    for (int i = 0; i < N; ++i) {
        double u1 = g.tasainen(), u2 = g.tasainen();
        if (tapa == Tapa::tasainen) {
            Vec3 w = tasainen_puolipallo(u1, u2);
            s += taivas(w) * w.z * (2 * PII);         // pdf = 1 / 2 pi
        } else {
            Vec3 w = kosinipainotettu(u1, u2);
            if (tapa == Tapa::kosini)
                s += taivas(w) * PII;                 // pdf = cos / pi
            else
                s += taivas(w) * w.z * (2 * PII);     // väärä pdf!
        }
    }
    return s / N;
}
// @loppu estimaattorit

int main() {
    // @alku virhe
    // Jokaiselle N:lle 400 toisistaan riippumatonta estimaattia:
    // keskiarvo paljastaa harhan ja RMSE kokonaisvirheen.
    std::printf("tarkka E = %.4f\n", TARKKA);
    std::printf("     N  tasainen RMSE  kosini RMSE  RMSE*sqrt(N)  "
                "väärä pdf: ka\n");
    for (int N : {4, 16, 64, 256, 1024}) {
        double v[3] = {}, ka[3] = {};
        for (int k = 0; k < 400; ++k)
            for (int t = 0; t < 3; ++t) {
                Pcg32 g(static_cast<std::uint64_t>(N) * 1000 + k,
                        static_cast<std::uint64_t>(t));
                double e = estimaatti(static_cast<Tapa>(t), N, g);
                v[t] += (e - TARKKA) * (e - TARKKA) / 400;
                ka[t] += e / 400;
            }
        std::printf("%6d  %13.4f  %11.4f  %5.2f / %5.2f  %13.4f\n", N,
                    std::sqrt(v[0]), std::sqrt(v[1]),
                    std::sqrt(v[0] * N), std::sqrt(v[1] * N), ka[2]);
    }
    // @loppu virhe
}
