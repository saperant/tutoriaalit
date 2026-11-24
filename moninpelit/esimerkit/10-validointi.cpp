// Palvelimen auktoriteetti: asiakas lähettää aikeensa (syötteet), ei
// lopputulosta (sijaintia). Palvelin rajaa syötteet ja niiden määrän.
#include <algorithm>
#include <cstdint>
#include <print>
#include <vector>

constexpr int TIKKEJA = 500;   // 10 s 50 tikillä sekunnissa
constexpr int NOPEUS = 10;     // cm tikissä

struct Syote {
    int dx, dy;     // aiottu suunta, rehellisellä -1..1
    int x, y;       // asiakkaan väittämä sijainti
};

// Asiakkaan lähettämät syötteet yhden tikin aikana; x ja y ovat
// asiakkaan oma käsitys sijainnistaan.
std::vector<Syote> asiakas(int tapa, int tikki, int x, int y) {
    switch (tapa) {
    case 1:  // teleporttaus: väittää olevansa maalissa
        return {{1, 0, 99'999, 0}};
    case 2:  // nopeushuijaus: kolme syötettä joka tikki
        return {{1, 0, x + NOPEUS, y}, {1, 0, x + 2 * NOPEUS, y},
                {1, 0, x + 3 * NOPEUS, y}};
    case 3:  // muokattu syöte: suuntavektorin pituus 10
        return {{10, 0, x + 10 * NOPEUS, y}};
    default:  // rehellinen, joka viides tikki tauko
        return {{tikki % 5 ? 1 : 0, 0, x + (tikki % 5 ? NOPEUS : 0), y}};
    }
}

// @alku tarkistus
// Palvelimen syötebudjetti: yksi syöte tikissä, pieni varasto
// verkon värinää varten (merkkiämpäri).
struct Budjetti {
    int merkit = 3;
    bool kuluta() {
        if (merkit == 0) {
            return false;
        }
        --merkit;
        return true;
    }
    void tikki() { merkit = std::min(merkit + 1, 3); }
};

int rajaa(int v) { return std::clamp(v, -1, 1); }
// @loppu tarkistus

int main() {
    const char* nimet[] = {"rehellinen", "teleporttaus", "nopeushuijaus",
                           "iso vektori"};
    std::println("{:<14} {:>16} {:>16} {:>9}", "pelaaja", "asiakas päättää",
                 "palvelin päättää", "hylätty");
    for (int tapa = 0; tapa < 4; ++tapa) {
        int luotettu_x = 0, x = 0, hylatty = 0;
        Budjetti budjetti;
        for (int tikki = 0; tikki < TIKKEJA; ++tikki) {
            budjetti.tikki();
            for (const Syote& s : asiakas(tapa, tikki, luotettu_x, 0)) {
                luotettu_x = s.x;  // naiivi: uskotaan asiakasta
                // @alku palvelin
                if (!budjetti.kuluta()) {
                    ++hylatty;  // liikaa syötteitä
                    continue;
                }
                if (s.dx != rajaa(s.dx) || s.dy != rajaa(s.dy)) {
                    ++hylatty;  // mahdoton syöte: kirjataan ja rajataan
                }
                x += rajaa(s.dx) * NOPEUS;  // y vastaavasti
                // @loppu palvelin
            }
        }
        std::println("{:<14} {:>13} cm {:>13} cm {:>9}", nimet[tapa],
                     luotettu_x, x, hylatty);
    }
}
