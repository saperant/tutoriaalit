// Epäyhtenäinen skaala vanhemmassa vääristää kierrettyä lasta: lapsen
// akselit eivät ole enää kohtisuorassa, eikä maailmamatriisia voi
// esittää siirtona, kiertona ja skaalana.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku koe
void koe(const char* nimi, Vec3 vanhemman_skaala) {
    Muunnos vanhempi{{0, 0, 0}, {}, vanhemman_skaala};
    Muunnos lapsi{{0, 0, 0}, akselikulma({0, 0, 1}, rad(45)), {1, 1, 1}};
    Mat4 maailma = matriisi(vanhempi) * matriisi(lapsi);
    Vec3 x = muunna_suunta(maailma, {1, 0, 0});
    Vec3 y = muunna_suunta(maailma, {0, 1, 0});
    double kulma = aste(std::acos(piste(x, y) / (pituus(x) * pituus(y))));
    // Yritetään palauttaa matriisi osiksi ja takaisin matriisiksi.
    Mat4 takaisin = matriisi(hajota(maailma));
    double virhe = 0;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            virhe = std::max(virhe,
                             std::abs(takaisin.m[i][j] - maailma.m[i][j]));
    std::println("{:17} akselien kulma {:>6} astetta, "
                 "hajotuksen virhe {}",
                 nimi, luku(kulma, 1), luku(virhe));
}
// @loppu koe

int main() {
    koe("skaala (2, 2, 2)", {2, 2, 2});
    koe("skaala (3, 1, 1)", {3, 1, 1});
}
