// Kvaternion perusoperaatiot: akseli ja kulma, yhdistäminen, vektorin
// kierto, q ja -q sekä kulmanopeuden integrointi ja normalisointi.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

std::string teksti(Kvat q) {
    return std::format("({}, {}, {}, {})", luku(q.w, 3), luku(q.x, 3),
                       luku(q.y, 3), luku(q.z, 3));
}

int main() {
    // @alku perus
    Kvat q = akselikulma({0, 1, 0}, rad(90));  // neljänneskierros y:n ympäri
    std::println("q = {}", teksti(q));
    std::println("x-akseli kierrettynä: {}", teksti(kierra(q, {1, 0, 0})));
    std::println("takaisin liittoluvulla: {}",
                 teksti(kierra(liitto(q), kierra(q, {1, 0, 0}))));
    Kvat miinus{-q.w, -q.x, -q.y, -q.z};
    std::println("-q kiertää samoin: {}", teksti(kierra(miinus, {1, 0, 0})));
    // @loppu perus

    // @alku yhdistaminen
    // Tulo vastaa matriisituloa: oikeanpuoleinen kierto tehdään ensin.
    Kvat a = akselikulma({0, 1, 0}, rad(90));
    Kvat b = akselikulma({1, 0, 0}, rad(90));
    Vec3 v{0, 0, -1};
    std::println("\na * b: {}   matriiseilla: {}", teksti(kierra(a * b, v)),
                 teksti(muunna_suunta(matriisiksi(a) * matriisiksi(b), v)));
    std::println("b * a: {}", teksti(kierra(b * a, v)));
    // @loppu yhdistaminen

    // @alku integrointi
    // Kappale pyörii kulmanopeudella w (rad/s) kymmenen sekuntia.
    // Askel: q += dt/2 * (0, w) * q. Summa ei ole yksikkökvaternio.
    Vec3 w{0, 2, 0};
    const double dt = 1.0 / 60;
    Kvat ilman, kanssa;
    for (int i = 0; i < 600; ++i) {
        for (Kvat* k : {&ilman, &kanssa}) {
            Kvat d = Kvat{0, w.x, w.y, w.z} * *k;
            *k = {k->w + dt / 2 * d.w, k->x + dt / 2 * d.x,
                  k->y + dt / 2 * d.y, k->z + dt / 2 * d.z};
        }
        kanssa = normalisoi(kanssa);
    }
    std::println("\nilman normalisointia: |q| = {}, "
                 "kierretyn yksikkövektorin pituus {}",
                 luku(std::sqrt(piste(ilman, ilman)), 3),
                 luku(pituus(kierra(ilman, {1, 0, 0})), 3));
    std::println("normalisoituna:       |q| = {}, "
                 "kierretyn yksikkövektorin pituus {}",
                 luku(std::sqrt(piste(kanssa, kanssa)), 3),
                 luku(pituus(kierra(kanssa, {1, 0, 0})), 3));
    // @loppu integrointi
}
