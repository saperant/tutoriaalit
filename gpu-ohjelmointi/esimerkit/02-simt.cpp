// SIMT-malli CPU:lla: 32 kaistan ryhmä (warp, aalto) suorittaa saman
// käskyn kerrallaan. Haarautuminen suoritetaan maskeilla, joten
// kumpikin haara maksaa, jos yksikin kaista menee kumpaankin.
#include <array>
#include <bitset>
#include <functional>
#include <print>

constexpr int kaistoja = 32;
using Maski = std::bitset<kaistoja>;

// @alku malli
struct Ryhma {
    int kaskyja = 0;          // suoritetut käskyt (koko ryhmä kerrallaan)
    int aktiivisia = 0;       // hyödyllinen työ: aktiiviset kaistat
};

// Käsky suoritetaan kaikille kaistoille; maski kertoo, mitkä
// kaistat kirjoittavat tuloksensa. Muut odottavat tyhjän panttina.
void suorita(Ryhma& r, Maski maski, int kaskyja) {
    if (maski.none()) {
        return;  // haara ohitetaan, jos yksikään kaista ei mene sinne
    }
    r.kaskyja += kaskyja;
    r.aktiivisia += kaskyja * static_cast<int>(maski.count());
}

// if (ehto) { 20 käskyä } else { 20 käskyä } 64 säikeelle, eli
// kahdelle ryhmälle. Ehto riippuu säikeen globaalista indeksistä.
Ryhma haarautuva(const std::function<bool(int)>& ehto) {
    Ryhma r;
    for (int ryhma = 0; ryhma < 2; ++ryhma) {
        Maski tosi;
        for (int kaista = 0; kaista < kaistoja; ++kaista) {
            tosi[static_cast<std::size_t>(kaista)] =
                ehto(ryhma * kaistoja + kaista);
        }
        suorita(r, Maski{}.set(), 2);  // ehdon laskenta
        suorita(r, tosi, 20);          // then-haara
        suorita(r, ~tosi, 20);         // else-haara
    }
    return r;
}
// @loppu malli

int main() {
    // @alku kokeet
    struct Koe {
        const char* nimi;
        std::function<bool(int)> ehto;
    };
    const std::array<Koe, 4> kokeet{{
        {"i < 32 (ryhmän raja)", [](int i) { return i < 32; }},
        {"i < 16              ", [](int i) { return i < 16; }},
        {"i % 2 == 0          ", [](int i) { return i % 2 == 0; }},
        {"i != 7              ", [](int i) { return i != 7; }},
    }};
    for (const auto& koe : kokeet) {
        const Ryhma r = haarautuva(koe.ehto);
        const double kaytto =
            100.0 * r.aktiivisia / (r.kaskyja * kaistoja);
        std::println("{}: {:2} käskyä, kaistojen käyttöaste {:5.1f} %",
                     koe.nimi, r.kaskyja, kaytto);
    }
    // @loppu kokeet
}
