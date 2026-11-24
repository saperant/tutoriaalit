// Varjosäteet ja itseleikkaus ("shadow acne"): kolme tapaa aloittaa
// varjosäde pinnalta.
#include <cstdio>
#include <vector>

#include "yhteinen/kamera.hpp"
#include "yhteinen/kuva.hpp"

const int L = 48, K = 36;
const Vec3 AURINKO = normalisoi({-0.6, 1, -0.3});  // pinnasta valoon

enum class Tapa { ei_mitaan, tmin, normaali };

// @alku varjo
// Osuma ja varjosäde kohtauksessa, joka on siirretty kohtaan X.
// Varjosäteen alku valitaan kolmella tavalla.
struct Tulos {
    bool osui = false, valaistu = false;
    double cos = 0;  // Lambertin kerroin
};
Tulos jaljita(const Sade& s, double X, Tapa tapa) {
    Pallo pallo{{X, 0.5, 0}, 0.5};
    Taso lattia{{0, 1, 0}, 0};
    double tp = leikkaa_pallo(pallo, s, 0, AARETON);
    double tl = leikkaa_taso(lattia, s, 0, tp);
    double t = std::min(tp, tl);
    if (t == AARETON) return {};
    Vec3 p = kohta(s, t);
    Vec3 n = tl < tp ? lattia.n : normalisoi(p - pallo.keski);
    double c = piste(n, AURINKO);
    if (c <= 0) return {true, false};          // pinta poispäin valosta
    double tmin = 0;
    if (tapa == Tapa::tmin) tmin = 1e-4;
    if (tapa == Tapa::normaali) p = p + 1e-7 * n;
    Sade varjo{p, AURINKO};
    bool este = leikkaa_pallo(pallo, varjo, tmin, AARETON) < AARETON ||
                leikkaa_taso(lattia, varjo, tmin, AARETON) < AARETON;
    return {true, !este, c};
}
// @loppu varjo

int main() {
    Kehys kuva(3 * L, K);
    // @alku main
    std::printf("valaistuja pikseleitä\n");
    std::printf("        X  ei siirtoa  tmin 1e-4  normaali 1e-7\n");
    for (double X : {0.0, 1e8, 1e11}) {
        Kamera k = kamera({X + 0.3, 0.9, -1.5}, {X, 0.35, 0}, {0, 1, 0},
                          1.6, L, K);
        std::vector<int> valaistu(3, 0);
        for (int i = 0; i < 3; ++i)
            for (int y = 0; y < K; ++y)
                for (int x = 0; x < L; ++x) {
                    Tulos r = jaljita(k.sade(x + 0.5, y + 0.5), X,
                                      static_cast<Tapa>(i));
                    valaistu[i] += r.valaistu;
                    if (X == 0) {
                        double v = !r.osui      ? 0.2
                                    : r.valaistu ? 0.05 + 0.7 * r.cos
                                                 : 0.05;
                        kuva(i * L + x, y) = {v, v, v};
                    }
                }
        std::printf("%9.0e  %10d  %9d  %13d\n", X, valaistu[0],
                    valaistu[1], valaistu[2]);
    }
    // @loppu main
    raportti("paneelit", kuva);
    ascii(kuva, 3, 4);
    tallenna_ppm(kuva, "03-akne.ppm");
}
