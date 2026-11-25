// Kipinä ilman ikkunaa: syöte luetaan tallenteesta, peli ajetaan
// kiinteällä aika-askeleella, ja lopputila tarkistetaan.
//
// Tallenteen rivit: "ruutuja toiminnot", esim. "30 OA" = 30 ruutua
// oikealle ja alas (V = vasen, O = oikea, Y = ylös, A = alas, - = ei).
#include "peli.hpp"
#include "piirto.hpp"

#include <iostream>
#include <print>
#include <string>

int main() {
    Peli peli(2026);
    Kuvapuskuri kuva;
    // @alku silmukka
    int ruutuja = 0;
    std::string napit;
    while (std::cin >> ruutuja >> napit && !peli.ohi) {
        const Syote s{napit.contains('V'), napit.contains('O'),
                      napit.contains('Y'), napit.contains('A')};
        for (int i = 0; i < ruutuja && !peli.ohi; ++i) {
            peli.paivita(s);
            for (Tapahtuma t : peli.tapahtumat) {
                if (t == Tapahtuma::Osuma) {
                    std::println("ruutu {:4}: osuma, elämiä {}",
                                 peli.ruutu, peli.elamat);
                } else if (t == Tapahtuma::PeliPaattyi) {
                    std::println("ruutu {:4}: peli päättyi", peli.ruutu);
                }
            }
        }
    }
    piirra(peli, kuva);
    // @loppu silmukka
    kuva.tallenna_ppm("kipina.ppm");
    std::println("ruutuja {}, pisteet {}, elämiä {}, miinoja {}",
                 peli.ruutu, peli.pisteet, peli.elamat, peli.miinat.size());
    std::println("tilan tarkistussumma {:016x}", peli.tarkistussumma());
    std::println("kuvan tarkistussumma {:08x}", kuva.tarkistussumma());
}
