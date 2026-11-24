// Polunseuranta Cornellin laatikossa: pelkkä BRDF-näytteistys vs.
// suora valaistus valon näytteellä (NEE).
#include <cstdio>

#include "yhteinen/cornell.hpp"
#include "yhteinen/polku.hpp"

#ifdef KUVITUS   // make kuvat: suurempi kuva tähän dokumenttiin
const int L = 160, K = 120, N_KUVA = 256;
#else
const int L = 40, K = 30, N_KUVA = 16;
#endif

int main() {
    // @alku main
    Kohtaus K_ = cornell({}, {.vari = {0.2, 0.3, 0.75}});
    Kamera k = cornell_kamera(L, K);
    // Vertailuissa valo piirretään mustana: muuten sen reunapikselit,
    // 25 kertaa näytön valkoista kirkkaammat, hallitsisivat virhettä.
    Asetukset nee{.nayta_valot = false};
    Asetukset naiivi{.suora = false, .nayta_valot = false};
    Laskuri lv;
    Kehys vertailu = renderoi(K_, k, 128, 1, nee, lv);
    raportti("vertailu 128", vertailu);
    std::printf("menetelmä    näytteitä  RMSE    keskiarvo  säteitä/näyte\n");
    for (int n : {4, 16}) {
        for (bool suora : {false, true}) {
            Laskuri l;
            Kehys kuva = renderoi(K_, k, n, 2, suora ? nee : naiivi, l);
            std::printf("%-12s %9d  %.4f  %9.4f  %13.2f\n",
                        suora ? "NEE" : "naiivi", n, rmse(kuva, vertailu),
                        keskiarvo(kuva),
                        static_cast<double>(l.sateet) / l.polut);

        }
    }
    Laskuri lk;
    Kehys kuva = renderoi(K_, k, N_KUVA, 3, {}, lk);
    raportti("NEE, valo näkyy", kuva);
    ascii(kuva, 2, 3);
    tallenna_ppm(kuva, "08-polku.ppm");
    // @loppu main
}
