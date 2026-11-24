// Rollback-verkkokoodi (GGPO-periaate): peli ei odota vastustajan
// syötettä vaan arvaa sen (toistaa edellisen). Kun oikea syöte saapuu ja
// arvaus oli väärä, palataan tallennettuun tilaan ja simuloidaan
// ruudut uudelleen. Pieni syöteviive vähentää palauttamisia.
#include <algorithm>
#include <array>
#include <cstdint>
#include <print>
#include <vector>

#include "yhteinen/kaksintaistelu.hpp"
#include "yhteinen/verkko.hpp"

constexpr int RUUTU_MS = 16;
constexpr int RUUTUJA = 3600;

std::vector<Syote> syotteet(std::uint64_t siemen) {
    Pcg32 r(siemen);
    std::vector<Syote> v(RUUTUJA + 64);
    Syote s = 0;
    for (Syote& x : v) {
        if (r.valilta(15) == 0) {
            s = static_cast<Syote>(r.valilta(8));
        }
        x = s;
    }
    return v;
}

struct Viesti {
    int ruutu;
    Syote syote;
};

int main() {
    const auto oma = syotteet(1), vastustaja = syotteet(2);
    Tila viite;
    for (int f = 0; f < RUUTUJA; ++f) {
        askel(viite, {oma[f], vastustaja[f]});
    }
    std::println("viite: {:08x}", tarkistussumma(viite));
    std::println("{:>11} {:>10} {:>14} {:>8} {:>9}", "syöteviive",
                 "palautuksia", "uudelleen/s", "syvin", "summa");
    for (int viive : {0, 1, 2, 3}) {
        Kanava<Viesti> kanava({.viive_ms = 40, .varina_ms = 15}, 8);
        std::vector<Tila> tilat(RUUTUJA + 1);  // tila ennen ruutua f
        std::vector<Syote> kaytetty(RUUTUJA), tiedetty(RUUTUJA);
        std::vector<bool> varma(RUUTUJA, false);
        Syote viimeisin_varma = 0;
        int ruutu = 0, palautuksia = 0, uudelleen = 0, syvin = 0;
        for (std::int64_t t = 0; ruutu < RUUTUJA || t < 70'000; ++t) {
            if (t % RUUTU_MS == 0) {
                const int f = static_cast<int>(t / RUUTU_MS) + viive;
                if (f < RUUTUJA) {
                    kanava.laheta(t, {f, vastustaja[f]});
                }
            }
            // @alku saapuminen
            int palaa = ruutu;  // aikaisin ruutu, jonka arvaus oli väärä
            for (const Viesti& v : kanava.vastaanota(t)) {
                varma[v.ruutu] = true;
                tiedetty[v.ruutu] = v.syote;
                if (v.ruutu < ruutu && kaytetty[v.ruutu] != v.syote) {
                    palaa = std::min(palaa, v.ruutu);
                }
            }
            if (palaa < ruutu) {
                // Palautus: tila ennen väärin arvattua ruutua ja
                // ruudut uudelleen parhailla tiedossa olevilla syötteillä.
                ++palautuksia;
                syvin = std::max(syvin, ruutu - palaa);
                Syote arvaus = palaa > 0 ? kaytetty[palaa - 1] : 0;
                for (int f = palaa; f < ruutu; ++f) {
                    arvaus = varma[f] ? tiedetty[f] : arvaus;
                    kaytetty[f] = arvaus;
                    tilat[f + 1] = tilat[f];
                    askel(tilat[f + 1], {oma[f], kaytetty[f]});
                    ++uudelleen;
                }
            }
            // @loppu saapuminen
            // @alku ruutu
            // Ruutu lasketaan aikataulussa ilman odottamista.
            // Syöteviive: painallus hetkellä T koskee ruutua T + viive,
            // joten syöte lähtee verkkoon viiveen verran etukäteen.
            const std::int64_t ajoaika = std::int64_t{ruutu} * RUUTU_MS;
            if (ruutu < RUUTUJA && t >= ajoaika) {
                for (int f = std::max(0, ruutu - 64); f < ruutu; ++f) {
                    if (varma[f]) {
                        viimeisin_varma = tiedetty[f];
                    }
                }
                kaytetty[ruutu] =
                    varma[ruutu] ? tiedetty[ruutu] : viimeisin_varma;
                tilat[ruutu + 1] = tilat[ruutu];
                askel(tilat[ruutu + 1], {oma[ruutu], kaytetty[ruutu]});
                ++ruutu;
            }
            // @loppu ruutu
        }
        std::println("{:>8} rt {:>10} {:>14} {:>5} rt {:>9x}", viive,
                     palautuksia, uudelleen / 60, syvin,
                     tarkistussumma(tilat[RUUTUJA]));
    }
}
