// Vartija: luvun 4 tilakone, joka havaitsee näkölinjalla ja liikkuu
// reitinhaulla. Pelaajan liikkeet on tallennettu, joten ajo toistuu.
#include "yhteinen/reitinhaku.hpp"

#include <array>
#include <cstdlib>
#include <print>
#include <string>

constexpr std::array<std::string_view, 10> RIVIT = {
    "######################",
    "#.........#....#.....#",
    "#.........#....#.###.#",
    "#..............#.....#",
    "#.........#....#.....#",
    "#####.#####..........#",
    "#.........#..........#",
    "#.........#..........#",
    "#....................#",
    "######################",
};

// @alku nakolinja
// Näkölinja Bresenhamin viivalla: käydään läpi ruudut a:sta b:hen ja
// lopetetaan ensimmäiseen esteeseen.
bool nakee(const Kartta& k, Ruutu a, Ruutu b, int kantama) {
    if (manhattan(a, b) > kantama) {
        return false;
    }
    const int dx = std::abs(b.x - a.x), dy = -std::abs(b.y - a.y);
    const int sx = a.x < b.x ? 1 : -1, sy = a.y < b.y ? 1 : -1;
    int virhe = dx + dy;
    while (a != b) {
        if (k.hinta(a) == 0) {
            return false;
        }
        const int e2 = 2 * virhe;
        if (e2 >= dy) {
            virhe += dy;
            a.x += sx;
        }
        if (e2 <= dx) {
            virhe += dx;
            a.y += sy;
        }
    }
    return true;
}
// @loppu nakolinja

// @alku vartija
enum class Tila { Partio, TakaaAjo, Etsinta };

constexpr int NAKO = 7;     // ruutua
constexpr int ODOTUS = 4;   // askelta viimeisessä havaintopaikassa
constexpr std::array<Ruutu, 2> PARTIO = {Ruutu{2, 2}, Ruutu{8, 7}};

struct Vartija {
    Ruutu paikka;
    Tila tila = Tila::Partio;
    std::size_t partiopiste = 0;
    Ruutu nahty{};  // pelaajan viimeisin havaittu ruutu
    int odotus = 0;
};

void paivita(Vartija& v, const Kartta& k, Ruutu pelaaja,
             bool liikkuu) {
    // 1) Havainto ja siirtymät.
    if (nakee(k, v.paikka, pelaaja, NAKO)) {
        v.tila = Tila::TakaaAjo;
        v.nahty = pelaaja;
    } else if (v.tila == Tila::TakaaAjo) {
        v.tila = Tila::Etsinta;
        v.odotus = ODOTUS;
    } else if (v.tila == Tila::Etsinta && v.paikka == v.nahty &&
               --v.odotus == 0) {
        v.tila = Tila::Partio;
    }
    // 2) Toiminta: tila päättää kohteen, reitinhaku seuraavan askeleen.
    if (v.tila == Tila::Partio && v.paikka == PARTIO[v.partiopiste]) {
        v.partiopiste = (v.partiopiste + 1) % PARTIO.size();
    }
    const Ruutu kohde =
        v.tila == Tila::Partio ? PARTIO[v.partiopiste] : v.nahty;
    const Reitti r = hae_reitti(k, v.paikka, kohde, manhattan);
    if (liikkuu && r.polku.size() > 1) {
        v.paikka = r.polku[1];
    }
}
// @loppu vartija

std::string_view nimi(Tila t) {
    switch (t) {
    case Tila::Partio: return "partio";
    case Tila::TakaaAjo: return "takaa-ajo";
    case Tila::Etsinta: return "etsintä";
    }
    return "?";
}

int main(int argc, char**) {
    const Kartta kartta{RIVIT};
    Vartija v{{2, 2}};
    Ruutu pelaaja{13, 3};
    // Pelaajan askeleet: v = vasen, o = oikea, y = ylös, a = alas,
    // . = paikallaan.
    const std::string_view liikkeet =
        ".vvvvvoooooaaoooyyyyoo..................";
    const bool kayra = argc > 1;  // käyrätila kuvitusta varten

    std::array<std::string, RIVIT.size()> kuva;
    for (std::size_t y = 0; y < RIVIT.size(); ++y) {
        kuva[y] = RIVIT[y];
    }
    auto merkitse = [&kuva](Ruutu r, char m) {
        kuva[static_cast<std::size_t>(r.y)][static_cast<std::size_t>(r.x)] =
            m;
    };

    Tila edellinen = v.tila;
    for (std::size_t askel = 0; askel < liikkeet.size(); ++askel) {
        const char l = liikkeet[askel];
        pelaaja.x += l == 'o' ? 1 : l == 'v' ? -1 : 0;
        pelaaja.y += l == 'a' ? 1 : l == 'y' ? -1 : 0;
        // Vartija on pelaajaa hitaampi: joka kolmas askel jää väliin.
        paivita(v, kartta, pelaaja, askel % 3 != 2);
        if (kayra) {
            std::println("{} {} {} {} {} {}", askel, nimi(v.tila),
                         v.paikka.x, v.paikka.y, pelaaja.x, pelaaja.y);
        } else if (v.tila != edellinen) {
            std::println("askel {:2}: {} -> {}, vartija ({}, {}), "
                         "pelaaja ({}, {})", askel, nimi(edellinen),
                         nimi(v.tila), v.paikka.x, v.paikka.y, pelaaja.x,
                         pelaaja.y);
        }
        edellinen = v.tila;
        merkitse(pelaaja, 'p');
        merkitse(v.paikka, 'v');
    }
    if (!kayra) {
        std::println("vartijan (v) ja pelaajan (p) jäljet:");
        for (const auto& rivi : kuva) {
            std::println("{}", rivi);
        }
    } else {
        for (const auto rivi : RIVIT) {
            std::println("kartta {}", rivi);
        }
    }
}
