// Suunta-albedo: kuinka suuren osan tulevasta valosta BRDF heijastaa.
// Energian säilyminen vaatii, että albedo on enintään 1.
#include <cstdio>

#include "yhteinen/materiaali.hpp"

// @alku albedo
// E(v) = int f(v, l) cos(theta_l) dl Monte Carlolla: poimi() palauttaa
// jo painon f cos / pdf, joten albedo on painojen keskiarvo.
double albedo(const Materiaali& m, double cos_v, int N = 20000) {
    Vec3 v{std::sqrt(1 - cos_v * cos_v), 0, cos_v};
    Pcg32 g(99);
    double s = 0;
    for (int i = 0; i < N; ++i) {
        Vec3 l;
        s += poimi(m, v, g, l).g;    // vihreä kanava riittää
    }
    return s / N;
}
// @loppu albedo

// @alku virheellinen
// Yleinen virhe: nimittäjästä puuttuu 4. Albedo tasaisella
// näytteistyksellä, joka ei riipu BRDF:n omasta poiminnasta.
double albedo_ilman_nelosta(double karheus, double cos_v) {
    Vec3 v{std::sqrt(1 - cos_v * cos_v), 0, cos_v};
    double alfa = karheus * karheus, s = 0;
    Pcg32 g(99);
    const int N = 200000;
    for (int i = 0; i < N; ++i) {
        double u1 = g.tasainen(), u2 = g.tasainen();
        Vec3 l = tasainen_puolipallo(u1, u2);
        Vec3 h = normalisoi(v + l);
        double f = ggx_d(h.z, alfa) * smith_g1(v.z, alfa) *
                   smith_g1(l.z, alfa) / (v.z * l.z);   // väärin
        s += f * l.z * 2 * PII;                          // pdf = 1/2pi
    }
    return s / N;
}
// @loppu virheellinen

int main() {
    // @alku main
    std::printf("valkoinen Lambert:    %.3f\n",
                albedo({.vari = {1, 1, 1}}, 0.7));
    std::printf("karheus  metalli cos 1  cos 0.3  eriste cos 1  cos 0.3"
                "  ilman 4:ää\n");
    for (double r : {0.1, 0.3, 0.5, 0.7, 1.0}) {
        Materiaali metalli{.laji = Materiaali::karhea,
                           .vari = {1, 1, 1}, .karheus = r, .metalli = 1};
        Materiaali eriste = metalli;
        eriste.metalli = 0;
        std::printf("%7.1f  %13.3f  %7.3f  %12.3f  %7.3f  %10.3f\n", r,
                    albedo(metalli, 1), albedo(metalli, 0.3),
                    albedo(eriste, 1), albedo(eriste, 0.3),
                    albedo_ilman_nelosta(r, 1));
    }
    // @loppu main
}
