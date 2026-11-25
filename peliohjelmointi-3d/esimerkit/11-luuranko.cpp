// Luuranko ja skinnaus: kolmen nivelen käsivarsi, sidontapoosi, taivutus
// ja painojen vaikutus kyynärpään kohdalla. Argumenttina annetulla
// nimellä tallennetaan kuvat käsivarresta suorana ja taivutettuna.
#include "yhteinen/luuranko.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <string>
#include <vector>

// @alku kasivarsi
// Käsivarsi x-akselin suuntaan: olkapää origossa, kyynärpää metrin
// päässä ja ranne siitä metrin päässä.
Luuranko kasivarsi() {
    Luuranko l;
    l.nivelet = {{"olkapää", -1, {{0, 1, 0}, {}, {1, 1, 1}}},
                 {"kyynärpää", 0, {{1, 0, 0}, {}, {1, 1, 1}}},
                 {"ranne", 1, {{1, 0, 0}, {}, {1, 1, 1}}}};
    laske_sidonta(l);
    return l;
}
// @loppu kasivarsi

// @alku painot
// Verteksin painot sen x-koordinaatin mukaan. Kyynärpään (x = 1)
// ympärillä paino liukuu olkavarrelta kyynärvarrelle matkan leveys
// aikana; leveys 0 tekee jäykän sidonnan.
Painot painot(double x, double leveys) {
    double t = leveys > 0 ? std::clamp((x - 1) / leveys + 0.5, 0.0, 1.0)
                          : (x < 1 ? 0.0 : 1.0);
    return {{0, 1, 0, 0}, {1 - t, t, 0, 0}};
}
// @loppu painot

// Nelikulmainen putki käsivarren ympärille: renkaita x-akselin suunnassa.
struct Iho {
    Verkko verkko;
    std::vector<Painot> painot;
};
Iho iho(double leveys) {
    Iho i;
    const int renkaita = 25;
    const double r = 0.15;
    for (int k = 0; k < renkaita; ++k) {
        double x = 2.1 * k / (renkaita - 1);
        for (auto [y, z] : {std::pair{r, r}, {r, -r}, {-r, -r}, {-r, r}}) {
            i.verkko.pisteet.push_back({x, 1 + y, z});
            i.painot.push_back(painot(x, leveys));
        }
    }
    for (int k = 0; k + 1 < renkaita; ++k)
        for (int s = 0; s < 4; ++s) {
            int a = 4 * k + s, b = 4 * k + (s + 1) % 4;
            i.verkko.kolmiot.push_back({a, a + 4, b + 4});
            i.verkko.kolmiot.push_back({a, b + 4, b});
        }
    return i;
}

void tallenna(const std::string& polku, const Luuranko& l, const Poosi& p,
              double leveys) {
    Kuva kuva(360, 300, {150, 185, 225});
    Piirtaja piirtaja(kuva,
                      perspektiivi(1 / std::tan(rad(15)), 1.2, 0.1, 100) *
                          katse({1.3, 2.4, 5}, {1.1, 1.4, 0}, {0, 1, 0}));
    piirra_lattia(piirtaja, 4, 0.5, {120, 150, 110}, {135, 165, 120});
    Iho i = iho(leveys);
    std::vector<Mat4> skin = skinnausmatriisit(l, p);
    Verkko v = i.verkko;
    for (std::size_t k = 0; k < v.pisteet.size(); ++k)
        v.pisteet[k] = skinnaa(v.pisteet[k], i.painot[k], skin);
    piirra(piirtaja, v, yksikko(), {215, 170, 140});
    std::vector<Mat4> nivelet = nivelmatriisit(l, p);
    for (std::size_t k = 0; k < nivelet.size(); ++k) {  // luut ja nivelet
        Vec3 a = muunna_piste(nivelet[k], {0, 0, 0});
        Vec3 b = k + 1 < nivelet.size()
                     ? muunna_piste(nivelet[k + 1], {0, 0, 0})
                     : muunna_piste(nivelet[k], {0.1, 0, 0});
        piirtaja.viiva(a, b, {30, 30, 30}, true);
        piirtaja.viiva(a - Vec3{0, 0.06, 0}, a + Vec3{0, 0.06, 0},
                       {230, 30, 30}, true);
    }
    kuva.tallenna_ppm(polku);
}

int main(int argc, char** argv) {
    Luuranko l = kasivarsi();

    // @alku taivutus
    Poosi p = lepopoosi(l);
    p[1].kierto = akselikulma({0, 0, 1}, rad(90));  // kyynärpää koukkuun
    std::vector<Mat4> nivelet = nivelmatriisit(l, p);
    std::println("Nivelet taivutettuna:");
    for (std::size_t i = 0; i < nivelet.size(); ++i)
        std::println("  {:10} {}", l.nivelet[i].nimi,
                     teksti(muunna_piste(nivelet[i], {0, 0, 0})));
    // @loppu taivutus

    // @alku vertailu
    // Kaksi verteksiä kyynärpään kohdalta, käsivarren ylä- ja alapinnalta.
    std::vector<Mat4> skin = skinnausmatriisit(l, p);
    Vec3 yla{1, 1.15, 0}, ala{1, 0.85, 0};
    std::println("\nKyynärpään verteksit, käsivarren paksuus 0,30:");
    for (double leveys : {0.0, 0.5}) {
        Vec3 a = skinnaa(yla, painot(1, leveys), skin);
        Vec3 b = skinnaa(ala, painot(1, leveys), skin);
        std::println("  sekoitusalue {}: ylä {} ala {} paksuus {}",
                     luku(leveys, 1), teksti(a), teksti(b),
                     luku(pituus(a - b)));
    }
    // @loppu vertailu

    if (argc > 1) {
        std::string nimi = argv[1];
        tallenna(nimi + "-1.ppm", l, lepopoosi(l), 0.5);
        tallenna(nimi + "-2.ppm", l, p, 0.0);
        tallenna(nimi + "-3.ppm", l, p, 0.5);
    }
}
