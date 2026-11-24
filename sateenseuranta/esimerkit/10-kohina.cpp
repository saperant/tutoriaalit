// Kohinan poisto: laatikkosuodin ja reunat säilyttävä suodin, joka
// käyttää apupuskurina ensimmäisen osuman materiaalia ja normaalia.
#include <cstdio>
#include <vector>

#include "yhteinen/cornell.hpp"
#include "yhteinen/polku.hpp"

#ifdef KUVITUS   // make kuvat: suurempi kuva tähän dokumenttiin
const int L = 120, K = 90, VERTAILU = 1024;
#else
const int L = 40, K = 30, VERTAILU = 128;
#endif

// @alku apupuskuri
// Apupuskuri (G-puskuri): pikselin keskisäteen ensimmäinen osuma.
struct Apu {
    int m = -1;
    Vec3 n;
};
std::vector<Apu> apupuskuri(const Kohtaus& K_, const Kamera& k) {
    std::vector<Apu> a;
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            Osuma o = leikkaa(K_, k.sade(x + 0.5, y + 0.5));
            a.push_back({o.m, o.n});
        }
    return a;
}
// @loppu apupuskuri

// @alku suodin
// 5 x 5 -keskiarvo. Reunat säilyttävä versio ottaa mukaan vain
// naapurit, joilla on sama materiaali ja lähes sama normaali.
Kehys suodata(const Kehys& k, const std::vector<Apu>* apu) {
    Kehys tulos(L, K);
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            Vari summa{};
            int n = 0;
            const Apu* oma = apu ? &(*apu)[y * L + x] : nullptr;
            for (int dy = -2; dy <= 2; ++dy)
                for (int dx = -2; dx <= 2; ++dx) {
                    int xx = x + dx, yy = y + dy;
                    if (xx < 0 || yy < 0 || xx >= L || yy >= K) continue;
                    if (oma) {
                        const Apu& toinen = (*apu)[yy * L + xx];
                        if (toinen.m != oma->m ||
                            (oma->m >= 0 && piste(toinen.n, oma->n) < 0.9))
                            continue;
                    }
                    summa = summa + k(xx, yy);
                    ++n;
                }
            tulos(x, y) = (1.0 / n) * summa;
        }
    return tulos;
}
// @loppu suodin

int main() {
    // @alku main
    Kohtaus K_ = cornell({}, {.vari = {0.2, 0.3, 0.75}});
    Kamera k = cornell_kamera(L, K);
    Asetukset a{.nayta_valot = false};
    Laskuri l;
    Kehys vertailu = renderoi(K_, k, VERTAILU, 1, a, l);
    Kehys kohinainen = renderoi(K_, k, 2, 2, a, l);
    Kehys laatikko = suodata(kohinainen, nullptr);
    std::vector<Apu> apu = apupuskuri(K_, k);
    Kehys reunat = suodata(kohinainen, &apu);
    std::printf("RMSE vertailukuvaan\n");
    std::printf("2 näytettä               %.4f\n",
                rmse(kohinainen, vertailu));
    std::printf("laatikkosuodin 5 x 5     %.4f\n", rmse(laatikko, vertailu));
    std::printf("reunat säilyttävä 5 x 5  %.4f\n", rmse(reunat, vertailu));
    Kehys kuva(4 * L, K);
    const Kehys* paneelit[] = {&kohinainen, &laatikko, &reunat, &vertailu};
    for (int i = 0; i < 4; ++i)
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x)
                kuva(i * L + x, y) = (*paneelit[i])(x, y);
    ascii(kuva, 4, 4);
    tallenna_ppm(kuva, "10-kohina.ppm");
    // @loppu main
}
