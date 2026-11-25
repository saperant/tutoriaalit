// Nopea kappale ja ohut seinä: diskreetti törmäystunnistus päästää
// luodin läpi, jatkuva ei. Argumenttina annettuun tiedostoon
// kirjoitetaan luodin paikat askelittain.
#include "yhteinen/maailma.hpp"
#include "yhteinen/tulostus.hpp"

#include <fstream>
#include <print>

// @alku koe
// Pallo ammutaan kohti 10 cm paksua seinää. Palauttaa pallon
// x-koordinaatin sekunnin kuluttua: seinä on kohdassa x = 5.
double ammu(double vauhti, bool jatkuva, std::ofstream* loki = nullptr) {
    Maailma m;
    m.asetukset.painovoima = {};
    m.lisaa(tee_seina({0.05, 2, 2}, {5, 2, 0}));
    Kappale luoti = tee_pallo(0.1, 0.1, {0, 2, 0});
    luoti.nopeus = {vauhti, 0, 0};
    luoti.kimmoisuus = 0.5;
    luoti.nopea = jatkuva;
    int i = m.lisaa(luoti);
    for (int askel = 0; askel < 60; ++askel) {
        if (loki)
            *loki << jatkuva << " " << askel << " "
                  << m.kappaleet[i].sijainti.x << "\n";
        m.askel();
    }
    return m.kappaleet[i].sijainti.x;
}
// @loppu koe

int main(int argc, char** argv) {
    // @alku tulos
    // Askeleessa kuljettu matka on vauhti / 60. Pallo havaitaan vain,
    // jos jokin askel päättyy seinän sisään, ja se työnnetään oikealle
    // puolelle vain, jos keskipiste ei ole ehtinyt seinän puolivälin
    // ohi. Turvallinen matka on siis pallon säde + seinän puolipaksuus
    // = 0,15 m askeleessa.
    std::println("{:>8} {:>12} {:>12} {:>12}", "vauhti", "matka/askel",
                 "diskreetti", "jatkuva");
    for (double vauhti : {6.0, 12.0, 40.0, 150.0}) {
        double d = ammu(vauhti, false), j = ammu(vauhti, true);
        std::println("{:>8} {:>10} m {:>12} {:>12}", luku(vauhti, 0),
                     luku(vauhti / 60), d > 5 ? "läpi" : "kimposi",
                     j > 5 ? "läpi" : "kimposi");
    }
    // @loppu tulos

    // @alku aika
    // Osuma-aika suoraan: pallo 3 m:n päässä seinän pinnasta, siirtymä
    // askeleessa 4 m. Osuma tapahtuu, kun askeleesta on kulunut 3/4.
    Kappale seina = tee_seina({0.05, 2, 2}, {5, 2, 0});
    Kappale pallo = tee_pallo(0.1, 0.1, {1.85, 2, 0});
    std::println("\nosuma-aika askeleen osana: {}",
                 luku(osuma_aika(pallo, {4, 0, 0}, seina), 3));
    std::println("ohi lentävälle: {}",
                 luku(osuma_aika(pallo, {4, 0, 9}, seina), 3));
    // @loppu aika

    if (argc > 1) {
        std::ofstream f(argv[1]);
        ammu(40, false, &f);
        ammu(40, true, &f);
    }
}
