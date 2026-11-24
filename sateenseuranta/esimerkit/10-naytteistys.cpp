// Näytteiden sijoittelu: satunnainen, ositettu ja Haltonin jono.
#include <cmath>
#include <cstdio>
#include <initializer_list>

#include "yhteinen/satunnainen.hpp"

// @alku integrandi
// Pikselin peitto: osuus pikselistä, joka on reunan y < 0.3 + 0.4 x
// alapuolella. Tarkka arvo on 0.5. Tällainen epäjatkuva funktio on
// tyypillinen: kappaleen reuna, varjon raja tai tekstuurin sauma.
double peitto(double x, double y) { return y < 0.3 + 0.4 * x ? 1 : 0; }
// @loppu integrandi

// @alku sijoittelu
enum class Tapa { satunnainen, ositettu, halton };

// Estimaatti N:llä näytteellä. Haltonin pisteitä siirretään samalla
// satunnaisella vektorilla modulo 1 (Cranley–Patterson-kierto), jotta
// toistoista saadaan toisistaan riippumattomia.
double estimaatti(Tapa tapa, int N, Pcg32& g) {
    int sivu = static_cast<int>(std::sqrt(N));   // N on neliöluku
    double sx = g.tasainen(), sy = g.tasainen(), s = 0;
    for (int i = 0; i < N; ++i) {
        double x, y;
        if (tapa == Tapa::satunnainen) {
            x = g.tasainen();
            y = g.tasainen();
        } else if (tapa == Tapa::ositettu) {   // satunnainen piste ruudussa
            x = (i % sivu + g.tasainen()) / sivu;
            y = (i / sivu + g.tasainen()) / sivu;
        } else {
            x = std::fmod(halton(i + 1, 2) + sx, 1.0);
            y = std::fmod(halton(i + 1, 3) + sy, 1.0);
        }
        s += peitto(x, y);
    }
    return s / N;
}
// @loppu sijoittelu

int main() {
    // @alku main
    std::printf("RMSE 400 toistosta, tarkka arvo 0.5\n");
    std::printf("     N  satunnainen  ositettu   Halton\n");
    for (int N : {16, 64, 256, 1024}) {
        std::printf("%6d", N);
        for (int t = 0; t < 3; ++t) {
            double v = 0;
            for (int r = 0; r < 400; ++r) {
                Pcg32 g(static_cast<std::uint64_t>(r), N);
                double e = estimaatti(static_cast<Tapa>(t), N, g) - 0.5;
                v += e * e / 400;
            }
            std::printf("  %9.5f", std::sqrt(v));
        }
        std::printf("\n");
    }
    // @loppu main
}
