// Hahmo ja ruutukartta: liike ratkaistaan akseli kerrallaan, jolloin
// seinä pysäyttää vain vaakaliikkeen ja lattia vain pystyliikkeen.
// Koordinaatisto on ruudun: x oikealle, y alas, yksi ruutu = 1 m.
#include <algorithm>
#include <array>
#include <cmath>
#include <print>
#include <string>
#include <string_view>

struct V2 {
    double x, y;
};

constexpr std::array<std::string_view, 9> KARTTA = {
    "######################",
    "#....................#",
    "#....................#",
    "#....................#",
    "#..............###...#",
    "#....................#",
    "#........###.........#",
    "#....................#",
    "######################",
};

bool kiintea(int tx, int ty) {
    if (ty < 0 || ty >= static_cast<int>(KARTTA.size()) || tx < 0 ||
        tx >= static_cast<int>(KARTTA[0].size())) {
        return true;  // kartan ulkopuoli on seinää
    }
    return KARTTA[static_cast<std::size_t>(ty)]
               [static_cast<std::size_t>(tx)] == '#';
}

// @alku hahmo
struct Hahmo {
    V2 keski;       // laatikon keskipiste
    V2 puoli;       // puolikoko
    V2 nopeus;
    bool maassa = false;
};

// Ruudut, joita laatikko peittää. Pieni vara (IHO) estää sen, että
// täsmälleen reunaa koskettava laatikko tulkitaan päällekkäiseksi.
constexpr double IHO = 1e-9;

struct Ruutuvali {
    int x0, x1, y0, y1;
};

Ruutuvali peitto(const Hahmo& h) {
    return {static_cast<int>(std::floor(h.keski.x - h.puoli.x + IHO)),
            static_cast<int>(std::floor(h.keski.x + h.puoli.x - IHO)),
            static_cast<int>(std::floor(h.keski.y - h.puoli.y + IHO)),
            static_cast<int>(std::floor(h.keski.y + h.puoli.y - IHO))};
}
// @loppu hahmo

// @alku akselit
// Vaakaliike: jos laatikko päätyy kiinteään ruutuun, se siirretään
// ruudun reunaan tulosuunnan puolelle ja vaakanopeus nollataan.
bool liiku_x(Hahmo& h, double dx) {
    h.keski.x += dx;
    const Ruutuvali r = peitto(h);
    bool osui = false;
    for (int ty = r.y0; ty <= r.y1; ++ty) {
        for (int tx = r.x0; tx <= r.x1; ++tx) {
            if (!kiintea(tx, ty)) {
                continue;
            }
            h.keski.x = dx > 0.0 ? tx - h.puoli.x : tx + 1 + h.puoli.x;
            h.nopeus.x = 0.0;
            osui = true;
        }
    }
    return osui;
}

// Pystyliike samoin. Osuma alaspäin liikuttaessa tarkoittaa, että
// hahmo seisoo jonkin päällä.
bool liiku_y(Hahmo& h, double dy) {
    h.keski.y += dy;
    const Ruutuvali r = peitto(h);
    bool osui = false;
    for (int ty = r.y0; ty <= r.y1; ++ty) {
        for (int tx = r.x0; tx <= r.x1; ++tx) {
            if (!kiintea(tx, ty)) {
                continue;
            }
            h.keski.y = dy > 0.0 ? ty - h.puoli.y : ty + 1 + h.puoli.y;
            h.nopeus.y = 0.0;
            osui = true;
        }
    }
    h.maassa = osui && dy > 0.0;
    return osui;
}
// @loppu akselit

struct Syote {
    double suunta;  // -1, 0 tai +1
    bool hyppy;
};

// @alku askel
constexpr double DT = 1.0 / 60.0;
constexpr double PAINOVOIMA = 40.0;   // m/s² alaspäin (y kasvaa alas)
constexpr double HYPPYNOPEUS = 13.0;  // m/s, hyppy noin 2,1 m
constexpr double JUOKSU = 6.0;        // m/s

void askel(Hahmo& h, Syote s) {
    h.nopeus.x = s.suunta * JUOKSU;
    if (s.hyppy && h.maassa) {
        h.nopeus.y = -HYPPYNOPEUS;
    }
    h.nopeus.y += PAINOVOIMA * DT;  // semi-implisiittinen Euler
    liiku_x(h, h.nopeus.x * DT);
    liiku_y(h, h.nopeus.y * DT);
}
// @loppu askel

int main(int argc, char**) {
    const bool kayra = argc > 1;  // käyrätila kuvitusta varten
    Hahmo h{{2.5, 7.55}, {0.4, 0.45}, {0.0, 0.0}};
    std::array<std::string, KARTTA.size()> kuva;
    std::ranges::copy(KARTTA, kuva.begin());

    bool edellinen_maassa = true;
    double edellinen_vx = 0.0;
    for (int ruutu = 0; ruutu < 215; ++ruutu) {
        // Tallennettu syöte: juoksu oikealle, kolme hypyn painallusta ja
        // lopuksi juoksu seinää päin.
        const Syote s{1.0, ruutu == 55 || ruutu == 105 || ruutu == 140};
        const double pyydetty = s.suunta * JUOKSU;
        if (s.hyppy && !h.maassa && !kayra) {
            std::println("ruutu {:3}: hyppy ei onnistu ilmassa", ruutu);
        }
        askel(h, s);
        if (kayra) {
            std::println("{} {:.4f} {:.4f} {}", ruutu, h.keski.x,
                         h.keski.y, h.maassa ? 1 : 0);
            continue;
        }
        if (h.maassa != edellinen_maassa) {
            std::println("ruutu {:3}: {} ({:.2f}, {:.2f})", ruutu,
                         h.maassa ? "laskeutui" : "irtosi maasta",
                         h.keski.x, h.keski.y);
            edellinen_maassa = h.maassa;
        }
        if (h.nopeus.x == 0.0 && edellinen_vx != 0.0 && pyydetty != 0.0) {
            std::println("ruutu {:3}: osui seinään ({:.2f}, {:.2f})",
                         ruutu, h.keski.x, h.keski.y);
        }
        edellinen_vx = h.nopeus.x;
        if (ruutu % 5 == 0) {
            auto& merkki = kuva[static_cast<std::size_t>(h.keski.y)]
                               [static_cast<std::size_t>(h.keski.x)];
            if (merkki == '.') {
                merkki = 'o';
            }
        }
    }
    if (kayra) {
        for (const auto rivi : KARTTA) {
            std::println("kartta {}", rivi);
        }
        return 0;
    }
    std::println("lopussa ({:.2f}, {:.2f}), maassa: {}", h.keski.x,
                 h.keski.y, h.maassa);
    for (const auto& rivi : kuva) {
        std::println("{}", rivi);
    }
}
