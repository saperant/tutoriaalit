// Jäykän kappaleen tila ja massaominaisuudet: hitausmomentit,
// hitaustensori maailmassa, pisteen nopeus ja impulssin vaikutus.
#include "yhteinen/kappale.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

void tulosta(const char* nimi, const Mat3& a) {
    std::println("{}", nimi);
    for (int i = 0; i < 3; ++i)
        std::println("  {:>7} {:>7} {:>7}", luku(a.m[i][0], 3),
                     luku(a.m[i][1], 3), luku(a.m[i][2], 3));
}

int main() {
    // @alku hitaus
    Kappale pallo = tee_pallo(4.0, 0.5, {});
    Kappale lankku = tee_laatikko(4.0, {1.0, 0.1, 0.25}, {});
    std::println("pallo   I = {}", teksti(pallo.hitaus, 3));
    std::println("lankku  I = {}", teksti(lankku.hitaus, 3));
    // @loppu hitaus

    // @alku maailmassa
    lankku.kierto = akselikulma({0, 0, 1}, rad(30));
    tulosta("lankku 30 astetta kallellaan, I maailmassa:",
            hitaus_maailmassa(lankku));
    // @loppu maailmassa

    // @alku pisteen-nopeus
    lankku.kierto = {};
    lankku.nopeus = {1, 0, 0};
    lankku.kulmanopeus = {0, 2, 0};  // 2 rad/s pystyakselin ympäri
    for (Vec3 p : {Vec3{0, 0, 0}, Vec3{1, 0, 0}, Vec3{-1, 0, 0},
                   Vec3{0, 0, 0.25}})
        std::println("piste {:21} nopeus {}", teksti(p),
                     teksti(pisteen_nopeus(lankku, p)));
    // @loppu pisteen-nopeus

    // @alku impulssi
    // Sama impulssi kahteen kohtaan: keskelle ja lankun päähän.
    Vec3 j{0, 0, -2};  // N s
    for (Vec3 kohta : {Vec3{0, 0, 0}, Vec3{1, 0, 0}}) {
        Kappale k = tee_laatikko(4.0, {1.0, 0.1, 0.25}, {});
        anna_impulssi(k, j, kohta);
        std::println("impulssi kohtaan {}:", teksti(kohta));
        std::println("  nopeus {}  kulmanopeus {}", teksti(k.nopeus),
                     teksti(k.kulmanopeus));
        std::println("  liikemäärä {}  liike-energia {} J",
                     teksti(liikemaara(k)), luku(liike_energia(k), 3));
        std::println("  osumakohdan nopeus {}",
                     teksti(pisteen_nopeus(k, kohta)));
    }
    // @loppu impulssi
}
