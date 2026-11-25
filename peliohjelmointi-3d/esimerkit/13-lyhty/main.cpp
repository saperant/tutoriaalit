// Lyhty-pelin pääohjelma: ajaa pelin syötetiedoston mukaan kiinteällä
// askeleella ja tulostaa lokin. Argumenttina annetulla nimellä
// tallennetaan ruutuja kuviksi.
#include "peli.hpp"

#include "../yhteinen/tulostus.hpp"

#include <iostream>
#include <print>
#include <sstream>

int main(int argc, char** argv) {
    auto ladattu = lataa_peli();
    if (!ladattu) {
        std::println("lataus epäonnistui: {}", ladattu.error());
        return 1;
    }
    Peli peli = std::move(*ladattu);
    std::println("taso: {} kappaletta, {} törmäyskolmiota, {} lyhtyä",
                 peli.kappaleet.size(), peli.maailma.kolmiot().size(),
                 peli.lyhdyt.size());

    // @alku silmukka
    // Syötetiedoston rivi: kesto sekunteina, eteen, sivulle, kameran
    // kääntö (astetta/s) ja hyppy. Sama syöte tuottaa aina saman pelin.
    std::string rivi;
    int askelia = 0, kuva_nro = 0;
    while (std::getline(std::cin, rivi)) {
        if (rivi.empty() || rivi[0] == '#') continue;
        std::istringstream kentat(rivi);
        double kesto;
        Syote syote;
        kentat >> kesto >> syote.eteen >> syote.sivulle >>
            syote.kameran_kaanto >> syote.hyppy;
        for (int i = 0; i < std::lround(kesto / DT); ++i, ++askelia) {
            Syote s = syote;
            s.hyppy = syote.hyppy && i == 0;
            std::string keratty = paivita(peli, s);
            if (!keratty.empty())
                std::println("{:>6} s  {} kerätty", luku(peli.aika),
                             keratty);
            if (askelia % 60 == 59) {
                piirtolista(peli, 16.0 / 9);
                std::println("{:>6} s  hahmo {:22} {:7} kamera {} m, "
                             "näkyvissä {}/{}",
                             luku(peli.aika), teksti(peli.hahmo.jalat),
                             peli.hahmo.maassa ? "maassa" : "ilmassa",
                             luku(peli.kameran_etaisyys, 1), peli.nakyvia,
                             peli.kappaleet.size());
            }
            if (argc > 1 && askelia % 180 == 100) {
                Kuva kuva(480, 270, {150, 185, 225});
                piirra_ruutu(peli, kuva);
                kuva.tallenna_ppm(std::format("{}-{}.ppm", argv[1],
                                              ++kuva_nro));
            }
        }
    }
    // @loppu silmukka

    int kerattyja = 0;
    for (const Lyhty& l : peli.lyhdyt) kerattyja += l.keratty;
    std::println("loppu: {}/{} lyhtyä ajassa {} s", kerattyja,
                 peli.lyhdyt.size(), luku(peli.aika));
}
