// Pallon leikkauksen tarkkuus kaukana: koulukaava vs. vakaa muoto.
#include <cstdio>

#include "yhteinen/sade.hpp"

// @alku naiivi
// Suora toisen asteen kaava: t = (-B - sqrt(B^2 - 4AC)) / 2A.
double naiivi(const Pallo& p, const Sade& s) {
    Vec3 f = s.o - p.keski;
    double A = piste(s.d, s.d), B = 2 * piste(f, s.d);
    double C = piste(f, f) - p.r * p.r;
    double diskr = B * B - 4 * A * C;
    if (diskr < 0) return AARETON;
    return (-B - std::sqrt(diskr)) / (2 * A);
}
// @loppu naiivi

int main() {
    // @alku vertailu
    // Pieni pallo (r = 0.01) etäisyydellä D: tarkka osuma on D - r.
    // Säde kulkee keskipisteen ohi 0.6 r:n päästä, jolloin tarkka
    // t = D - 0.8 r.
    std::printf("  etäisyys   virhe naiivi    virhe vakaa\n");
    for (double D : {1e1, 1e3, 1e5, 1e7}) {
        Pallo p{{0, 0.006, D}, 0.01};
        Sade s{{0, 0, 0}, {0, 0, 1}};
        double tarkka = D - 0.008;
        double a = naiivi(p, s), b = leikkaa_pallo(p, s, 0, AARETON);
        auto virhe = [&](double t) {
            return t == AARETON ? AARETON : std::fabs(t - tarkka);
        };
        std::printf("%10.0e %14.2e %14.2e\n", D, virhe(a), virhe(b));
    }
    // @loppu vertailu
}
