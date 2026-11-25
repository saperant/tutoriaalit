// Kitka: kalteva taso, liukuva laatikko ja liukumisesta vierimiseen
// siirtyvä pallo. Tuloksia verrataan lukion fysiikan kaavoihin.
// Argumenttina annettuun tiedostoon kirjoitetaan pallon nopeuksien
// aikasarja.
#include "yhteinen/maailma.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>

const double G = 9.81;

// @alku rinne
// Laatikko lasketaan rinteelle levossa. Palauttaa sen kiihtyvyyden
// rinnettä alas mitattuna toisen sekunnin aikana.
double kiihtyvyys_rinteessa(double kulma_asteina, double kitka) {
    Maailma m;
    Kvat kallistus = akselikulma({0, 0, 1}, rad(-kulma_asteina));
    m.lisaa(tee_taso({}, kallistus));
    Kappale laatikko = tee_laatikko(1.0, {0.3, 0.2, 0.3}, {});
    laatikko.kierto = kallistus;
    laatikko.sijainti = kierra(kallistus, {0, 0.2, 0});
    laatikko.kitka = m.kappaleet[0].kitka = kitka;
    int i = m.lisaa(laatikko);
    Vec3 alas = kierra(kallistus, {1, 0, 0});
    double v1 = 0;
    for (int askel = 0; askel < 120; ++askel) {
        m.askel();
        if (askel == 59) v1 = piste(m.kappaleet[i].nopeus, alas);
    }
    return piste(m.kappaleet[i].nopeus, alas) - v1;  // dv sekunnissa
}
// @loppu rinne

// @alku liuku
// Laatikko liukuu vaakatasolla suuntaan (x, 0, z). Palauttaa matkan,
// jonka se kulkee ennen pysähtymistä.
double liukumatka(Vec3 suunta, double vauhti, double kitka) {
    Maailma m;
    m.lisaa(tee_taso());
    Kappale laatikko = tee_laatikko(1.0, {0.3, 0.05, 0.3}, {0, 0.05, 0});
    laatikko.nopeus = vauhti * normalisoi(suunta);
    laatikko.kitka = m.kappaleet[0].kitka = kitka;
    int i = m.lisaa(laatikko);
    for (int askel = 0; askel < 300; ++askel) m.askel();
    return pituus(m.kappaleet[i].sijainti - Vec3{0, 0.05, 0});
}
// @loppu liuku

int main(int argc, char** argv) {
    // @alku rinnetulos
    const double mu = 0.5;
    std::println("laatikko rinteessä, kitkakerroin {} (raja {} astetta):",
                 luku(mu, 1), luku(aste(std::atan(mu)), 1));
    for (double kulma : {15.0, 25.0, 30.0, 45.0}) {
        double teoria = std::max(
            0.0, G * (std::sin(rad(kulma)) - mu * std::cos(rad(kulma))));
        std::println("  {} astetta: kiihtyvyys {} m/s^2 (kaava {})",
                     luku(kulma, 0), luku(kiihtyvyys_rinteessa(kulma, mu)),
                     luku(teoria));
    }
    // @loppu rinnetulos

    // @alku liukutulos
    // Jarrutusmatka v^2 / (2 mu g) ei riipu suunnasta.
    double kaava = 4.0 * 4.0 / (2 * mu * G);
    std::println("\nliukumatka vauhdista 4 m/s (kaava {} m):",
                 luku(kaava));
    std::println("  akselin suuntaan   {} m",
                 luku(liukumatka({1, 0, 0}, 4, mu)));
    std::println("  vinottain          {} m",
                 luku(liukumatka({1, 0, 1}, 4, mu)));
    // @loppu liukutulos

    // @alku pallo
    // Pallo lähtee liukumaan pyörimättä. Kitka hidastaa etenemistä ja
    // kiihdyttää pyörimistä, kunnes pallo vierii: v = 5/7 v0.
    Maailma m;
    m.lisaa(tee_taso());
    Kappale pallo = tee_pallo(1.0, 0.5, {0, 0.5, 0});
    pallo.nopeus = {7, 0, 0};
    int i = m.lisaa(pallo);
    std::ofstream f;
    if (argc > 1) f.open(argv[1]);
    for (int askel = 0; askel <= 60; ++askel) {
        const Kappale& p = m.kappaleet[i];
        if (askel % 12 == 0)
            std::println("t = {} s: v = {}  w r = {}", luku(askel / 60.0, 1),
                         luku(p.nopeus.x), luku(-p.kulmanopeus.z * 0.5));
        if (f.is_open())
            f << askel / 60.0 << " " << p.nopeus.x << " "
              << -p.kulmanopeus.z * 0.5 << "\n";
        m.askel();
    }
    // @loppu pallo
}
