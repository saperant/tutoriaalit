// Radiometrian integraalit numeerisesti: kosini, BRDF:n albedo ja
// pinta-alavalon irradianssi.
#include <cmath>
#include <cstdio>

#include "yhteinen/naytteet.hpp"

// @alku puolipallo
// Pyörähdyssymmetrinen integraali pallonpuoliskon yli:
// int f(cos theta) d omega = 2 pi int_0^{pi/2} f(cos t) sin t dt.
// Keskipistesääntö N välillä.
template <class F>
double puolipallo(F f, int N = 2000) {
    double h = PII / 2 / N, s = 0;
    for (int i = 0; i < N; ++i) {
        double t = (i + 0.5) * h;
        s += f(std::cos(t)) * std::sin(t);
    }
    return 2 * PII * s * h;
}
// @loppu puolipallo

int main() {
    // @alku integraalit
    std::printf("int cos d omega        = %.5f (pi = %.5f)\n",
                puolipallo([](double c) { return c; }), PII);
    double rho = 0.8;
    std::printf("Lambert, rho = 0.8     albedo %.5f\n",
                puolipallo([&](double c) { return rho / PII * c; }));
    std::printf("Phong-lohko cos^n kohtisuoraan katsottuna:\n");
    std::printf("     n  normalisoimaton  normalisoitu\n");
    for (int n : {1, 10, 100, 1000}) {
        auto lohko = [n](double c) { return std::pow(c, n) * c; };
        double raaka = puolipallo(lohko);
        double kerroin = (n + 2) / (2 * PII);  // energian säilyminen
        std::printf("%6d  %15.5f  %12.5f\n", n, raaka, kerroin * raaka);
    }
    // @loppu integraalit

    // @alku pintavalo
    // Neliön muotoinen valo (sivu 1, radianssi 1) suoraan pisteen
    // yläpuolella korkeudella h. Tarkka irradianssi integroimalla
    // valon pinnan yli: dE = L cos_pinta cos_valo / r^2 dA.
    std::printf("valon korkeus  irradianssi  pistevalo L A / h^2  suhde\n");
    for (double h : {0.5, 1.0, 2.0, 5.0, 10.0}) {
        const int N = 400;
        double E = 0, dA = 1.0 / (N * N);
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j) {
                double x = (i + 0.5) / N - 0.5, z = (j + 0.5) / N - 0.5;
                double r2 = x * x + h * h + z * z;
                double c = h / std::sqrt(r2);   // molemmat kosinit
                E += c * c / r2 * dA;
            }
        double piste = 1.0 / (h * h);
        std::printf("%13.1f  %11.5f  %19.5f  %5.3f\n", h, E, piste,
                    E / piste);
    }
    // @loppu pintavalo
}
