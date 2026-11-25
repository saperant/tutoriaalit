// Animaatioleikkeet: avainkehysten näytteistys, kahden leikkeen
// sekoitus ja ristihäivytys leikkeestä toiseen.
#include "yhteinen/luuranko.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku leikkeet
Luuranko kasivarsi() {
    Luuranko l;
    l.nivelet = {{"olkapää", -1, {{0, 1, 0}, {}, {1, 1, 1}}},
                 {"kyynärpää", 0, {{1, 0, 0}, {}, {1, 1, 1}}},
                 {"ranne", 1, {{1, 0, 0}, {}, {1, 1, 1}}}};
    laske_sidonta(l);
    return l;
}
Kvat z_kierto(double asteet) { return akselikulma({0, 0, 1}, rad(asteet)); }

// Vilkutus: kyynärpää koukistuu ja ojentuu sekunnin jaksolla.
Leike vilkutus() {
    Kanava k{1, Kanava::Kohde::Kierto, {0, 0.5, 1}, {},
             {z_kierto(30), z_kierto(110), z_kierto(30)}};
    return {"vilkutus", 1.0, {k}};
}
// Nosto: olkapää nostaa koko käden kahdessa sekunnissa ylös ja takaisin.
Leike nosto() {
    Kanava k{0, Kanava::Kohde::Kierto, {0, 1, 2}, {},
             {z_kierto(0), z_kierto(60), z_kierto(0)}};
    return {"nosto", 2.0, {k}};
}
// @loppu leikkeet

// @alku ranne
Vec3 ranne(const Luuranko& l, const Poosi& p) {
    return muunna_piste(nivelmatriisit(l, p)[2], {0, 0, 0});
}
// @loppu ranne

int main() {
    Luuranko l = kasivarsi();
    Leike a = vilkutus(), b = nosto();

    // @alku naytteet
    std::println("Vilkutus: ranteen paikka");
    for (double t : {0.0, 0.25, 0.5, 0.75, 1.0, 1.25})
        std::println("  t = {}  {}", luku(t),
                     teksti(ranne(l, nayte(a, l, t))));
    // @loppu naytteet

    // @alku sekoitus
    std::println("\nHetki t = 0,5 eri painoilla (0 = vilkutus, 1 = nosto):");
    for (double w : {0.0, 0.5, 1.0})
        std::println("  paino {}  {}", luku(w, 1),
                     teksti(ranne(l, sekoita(nayte(a, l, 0.5),
                                             nayte(b, l, 0.5), w))));
    // @loppu sekoitus

    // @alku haivytys
    // Ristihäivytys: hetkestä 1,0 alkaen paino kasvaa 0,4 sekunnissa
    // nollasta yhteen. Molemmat leikkeet etenevät koko ajan.
    std::println("\nRistihäivytys vilkutuksesta nostoon:");
    for (double t : {0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5}) {
        double w = std::clamp((t - 1.0) / 0.4, 0.0, 1.0);
        Poosi p = sekoita(nayte(a, l, t), nayte(b, l, t), w);
        std::println("  t = {}  paino {}  ranne {}", luku(t, 1), luku(w),
                     teksti(ranne(l, p)));
    }
    // @loppu haivytys
}
