// Fresnelin heijastuskerroin: tarkka kaava ja Schlickin approksimaatio.
#include <cstdio>

#include "yhteinen/materiaali.hpp"

int main() {
    // @alku taulukko
    const double n = 1.5;                         // lasi
    const double f0 = (n - 1) * (n - 1) / ((n + 1) * (n + 1));
    std::printf("F0 = %.4f, kriittinen cos = %.4f\n", f0,
                std::sqrt(1 - 1 / (n * n)));
    std::printf(" cos_i   ilma->lasi  Schlick   lasi->ilma  Schlick\n");
    for (double c : {1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1,
                     0.05, 0.0}) {
        // Tiheämmästä aineesta Schlickin kaava käyttää taittunutta
        // kulmaa, koska heijastus on molempiin suuntiin sama.
        double sin2_t = n * n * (1 - c * c);
        double s_ulos = sin2_t >= 1 ? 1 : schlick(f0, std::sqrt(1 - sin2_t));
        std::printf("%6.2f  %10.4f  %8.4f  %10.4f  %8.4f\n", c,
                    fresnel(c, 1 / n), schlick(f0, c), fresnel(c, n),
                    s_ulos);
    }
    // @loppu taulukko
}
