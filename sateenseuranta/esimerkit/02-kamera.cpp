// Primäärisäteet: kolme palloa ja lattia, yksi ja 16 sädettä pikselissä.
#include <cstdio>

#include "yhteinen/kamera.hpp"
#include "yhteinen/kuva.hpp"
#include "yhteinen/satunnainen.hpp"

const int L = 64, K = 48;
const Pallo PALLOT[] = {{{-1.1, 0.5, 0}, 0.5}, {{0, 0.7, 0.6}, 0.7},
                        {{1.2, 0.4, -0.4}, 0.4}};
const Vari VARIT[] = {{0.8, 0.15, 0.1}, {0.8, 0.8, 0.8}, {0.1, 0.3, 0.8}};
const Taso LATTIA{{0, 1, 0}, 0};
const Vec3 VALO = normalisoi({-0.4, 1, -0.5});  // pinnasta valoon

// @alku sade
// Lähin osuma ja normaali; varjostus on pelkkä Lambert ilman varjoja.
Vari varjosta(const Sade& s) {
    double lahin = AARETON;
    Vec3 n;
    Vari vari;
    for (int i = 0; i < 3; ++i) {
        double t = leikkaa_pallo(PALLOT[i], s, 0, lahin);
        if (t < lahin) {
            lahin = t;
            n = normalisoi(kohta(s, t) - PALLOT[i].keski);
            vari = VARIT[i];
        }
    }
    double t = leikkaa_taso(LATTIA, s, 0, lahin);
    if (t < lahin) {
        lahin = t;
        n = LATTIA.n;
        Vec3 p = kohta(s, t);         // shakkiruudukko
        bool ruutu = (static_cast<int>(std::floor(p.x)) +
                      static_cast<int>(std::floor(p.z))) % 2 != 0;
        vari = ruutu ? Vari{0.5, 0.5, 0.5} : Vari{0.15, 0.15, 0.15};
    }
    if (lahin == AARETON) return {0.25, 0.35, 0.5};       // taivas
    double valo = std::max(0.0, piste(n, VALO));
    return (0.05 + 0.9 * valo) * vari;
}
// @loppu sade

// @alku jitter
// Pikselin väri n näytteen keskiarvona. Yksi näyte osuu pikselin
// keskelle; useampi näyte valitaan tasaisesti pikselin alueelta.
Kehys kuva(const Kamera& k, int n) {
    Kehys tulos(L, K);
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            Pcg32 g(2026, static_cast<std::uint64_t>(y) * L + x);
            Vari summa{};
            for (int i = 0; i < n; ++i) {
                double dx = n == 1 ? 0.5 : g.tasainen();
                double dy = n == 1 ? 0.5 : g.tasainen();
                summa = summa + varjosta(k.sade(x + dx, y + dy));
            }
            tulos(x, y) = (1.0 / n) * summa;
        }
    return tulos;
}
// @loppu jitter

int main() {
    // @alku main
    Kamera k = kamera({0, 1.4, -3}, {0, 0.5, 0}, {0, 1, 0}, 1.5, L, K);
    Sade keski = k.sade(L / 2.0, K / 2.0);
    std::printf("keskisäde suunta (%.3f, %.3f, %.3f)\n", keski.d.x,
                keski.d.y, keski.d.z);
    Kehys yksi = kuva(k, 1), kuusitoista = kuva(k, 16);
    raportti("1 näyte", yksi);
    raportti("16 näytettä", kuusitoista);
    std::printf("ero (RMSE) %.4f\n", rmse(yksi, kuusitoista));
    ascii(kuusitoista, 2, 4);
    tallenna_ppm(kuusitoista, "02-kamera.ppm");
    // @loppu main
}
