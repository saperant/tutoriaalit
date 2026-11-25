// Deterministinen lukitusaskel: koneet vaihtavat vain syötteitä, ja
// kumpikin simuloi saman pelin. Ruutu voidaan laskea vasta, kun
// molempien syötteet ovat perillä. Syöteviive antaa verkolle aikaa.
#include <algorithm>
#include <array>
#include <cstdint>
#include <map>
#include <print>
#include <vector>

#include "yhteinen/kaksintaistelu.hpp"
#include "yhteinen/verkko.hpp"

constexpr int RUUTU_MS = 16;
constexpr int RUUTUJA = 3600;  // minuutti 60 ruudulla sekunnissa

// Pelaajan syötteet: vaihtuvat keskimäärin 15 ruudun välein.
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
    std::uint32_t ruutu;
    Syote syote;
};

int main(int argc, char**) {
    loki_paalla = argc > 1;
    const auto oma = syotteet(1), vastustaja = syotteet(2);
    Tila viite;
    for (int f = 0; f < RUUTUJA; ++f) {
        askel(viite, {oma[f], vastustaja[f]});
    }
    std::println("viite: {:08x}", tarkistussumma(viite));
    const Linkki linkki{.viive_ms = 40, .varina_ms = 15};
    std::println("{:>6} {:>11} {:>14} {:>14} {:>9}", "viive", "syöteviive",
                 "myöhässä", "suurin", "summa");
    for (int viive : {0, 2, 4, 6}) {
        // @alku silmukka
        // Vastustajan syöte ruudulle f lähetetään ruudulla f - viive.
        Kanava<Viesti> kanava(linkki, 8);
        std::map<std::uint32_t, Syote> saadut;
        Tila tila;
        std::uint32_t ruutu = 0;
        std::int64_t myohassa = 0, suurin = 0, lahetetty = 0;
        for (std::int64_t t = 0; ruutu < RUUTUJA; ++t) {
            // Syötteet lähetetään viiveen verran etukäteen.
            while (lahetetty <= t / RUUTU_MS + viive &&
                   lahetetty < RUUTUJA) {
                const auto f = static_cast<std::uint32_t>(lahetetty);
                kanava.laheta(t, {f, vastustaja[f]});
                ++lahetetty;
            }
            for (const Viesti& v : kanava.vastaanota(t)) {
                saadut[v.ruutu] = v.syote;
                loki("S {} {} {}", viive, v.ruutu, t);  // kuvitusta varten
            }
            if (t < std::int64_t{ruutu} * RUUTU_MS) {
                continue;  // seuraavan ruudun aika ei ole vielä
            }
            const auto it = saadut.find(ruutu);
            if (it == saadut.end()) {
                continue;  // peli seisoo: syöte ei ole perillä
            }
            // Ensimmäinen sekunti on käynnistystä, sitä ei lasketa.
            const std::int64_t m = t - std::int64_t{ruutu} * RUUTU_MS;
            if (ruutu >= 60) {
                myohassa += m > 0;
                suurin = std::max(suurin, m);
            }
            loki("A {} {} {}", viive, ruutu, t);
            askel(tila, {oma[ruutu], it->second});
            ++ruutu;
        }
        // @loppu silmukka
        std::println("{:>3} rt {:>8} ms {:>7} ruutua {:>8} ms {:>9x}",
                     viive, viive * RUUTU_MS, myohassa, suurin,
                     tarkistussumma(tila));
    }
}
