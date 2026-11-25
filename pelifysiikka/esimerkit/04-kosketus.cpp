// Kapea vaihe: kosketuspisteet eri muotopareille. Argumenttina
// annettuun tiedostoon piirretään kuva, jossa kosketuspisteet ja
// normaalit näkyvät.
#include "yhteinen/kuvitus.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku rivi
void rivi(const char* nimi, const std::vector<Kappale>& k, int a, int b) {
    Monisto m = kosketa(k, a, b);
    if (m.pisteet.empty()) {
        std::println("{:27}ei kosketusta", nimi);
        return;
    }
    double syvin = -1;
    for (const Kosketuspiste& p : m.pisteet)
        syvin = std::max(syvin, p.syvyys);
    std::println("{:27}n = {:20} pisteitä {}, syvin {}", nimi,
                 teksti(m.normaali), m.pisteet.size(), luku(syvin, 3));
}
// @loppu rivi

int main(int argc, char** argv) {
    // @alku kappaleet
    std::vector<Kappale> k;
    k.push_back(tee_taso());                                     // 0
    k.push_back(tee_pallo(1, 0.5, {-4, 0.45, 0}));               // 1
    k.push_back(tee_pallo(1, 0.4, {-3.3, 0.6, 0}));              // 2
    k.push_back(tee_laatikko(1, {0.5, 0.5, 0.5}, {-1, 0.48, 0}));  // 3
    k.push_back(tee_laatikko(1, {0.5, 0.5, 0.5}, {-1, 1.46, 0}));  // 4
    k.push_back(tee_pallo(1, 0.3, {-1.6, 1.3, 0.4}));            // 5
    // Kulmallaan seisova laatikko: kierto vie lävistäjän pystyyn.
    k.push_back(tee_laatikko(1, {0.4, 0.4, 0.4}, {1, 0.68, 0}));   // 6
    k[6].kierto = akselikulma(normalisoi(Vec3{1, 0, -1}), rad(54.7356));
    // Kaksi lankkua ristikkäin päällekkäin.
    k.push_back(tee_laatikko(1, {1.0, 0.1, 0.2}, {3.2, 0.09, 0}));   // 7
    k.push_back(tee_laatikko(1, {1.0, 0.1, 0.2}, {3.2, 0.28, 0}));   // 8
    k[8].kierto = akselikulma({0, 1, 0}, rad(90));
    // Särmä särmää vastaan: kumpikin laatikko on kallellaan.
    k.push_back(tee_laatikko(1, {0.5, 0.3, 0.3}, {5.3, 1.0, 0}));    // 9
    k[9].kierto = akselikulma({1, 0, 0}, rad(45));
    k.push_back(tee_laatikko(1, {0.3, 0.3, 0.5}, {5.3, 1.8, 0}));    // 10
    k[10].kierto = akselikulma({0, 0, 1}, rad(45));
    // @loppu kappaleet

    // @alku testit
    rivi("taso - pallo", k, 0, 1);
    rivi("pallo - pallo", k, 1, 2);
    rivi("taso - laatikko", k, 0, 3);
    rivi("laatikko - laatikko", k, 3, 4);
    rivi("pallo - laatikko", k, 5, 4);
    rivi("laatikko - pallo", k, 4, 5);
    rivi("taso - laatikko kulmallaan", k, 0, 6);
    rivi("lankut ristikkäin", k, 7, 8);
    rivi("särmä - särmä", k, 9, 10);
    rivi("kaukana toisistaan", k, 3, 9);
    // @loppu testit

    if (argc > 1) {
        Maailma m;
        m.kappaleet = k;
        Kamera kamera{{0.8, 3.2, 8.5}, {0.8, 0.7, 0}, 40, 2.4};
        Kuva kuva(720, 300, TAIVAS);
        Piirtaja p(kuva, nakyma_projektio(kamera));
        piirra_maailma(p, m);
        auto parit = laaja_vaihe(k);
        for (auto [a, b] : parit) {
            Monisto mo = kosketa(k, a, b);
            for (const Kosketuspiste& piste : mo.pisteet) {
                p.viiva(piste.piste, piste.piste + 0.5 * mo.normaali,
                        {230, 30, 30}, true);
                p.viiva(piste.piste - Vec3{0.03, 0, 0},
                        piste.piste + Vec3{0.03, 0, 0}, {255, 240, 80},
                        true);
            }
        }
        kuva.tallenna_ppm(argv[1]);
    }
}
