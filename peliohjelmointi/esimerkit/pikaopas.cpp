// Pikaoppaan koodi: pelin perusrakenteet tiiviisti.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <print>

using namespace std::chrono_literals;

// @alku silmukka
constexpr auto ASKEL = 1'000'000'000ns / 60;  // kokonaislukuaika

struct Tila {
    double x = 0, vx = 0;
};

void paivita(Tila& t, double dt, bool oikealle) {
    t.vx += (oikealle ? 40.0 : 0.0) * dt;  // semi-implisiittinen Euler
    t.vx *= 0.98;                          // kitka
    t.x += t.vx * dt;
}

Tila sekoita(Tila a, Tila b, double alfa) {
    return {a.x + (b.x - a.x) * alfa, b.vx};
}
// @loppu silmukka

// @alku aabb
struct Aabb {
    double x, y, pw, ph;  // keskipiste ja puolikoko
};
bool limittain(const Aabb& a, const Aabb& b) {
    return std::abs(a.x - b.x) < a.pw + b.pw &&
           std::abs(a.y - b.y) < a.ph + b.ph;
}
// @loppu aabb

// @alku reuna
struct Nappi {
    bool nyt = false, ennen = false;
    void ruutu(bool alhaalla) { ennen = nyt; nyt = alhaalla; }
    bool painettu() const { return nyt && !ennen; }
};
// @loppu reuna

int main() {
    // @alku kaytto
    const double dt = std::chrono::duration<double>(ASKEL).count();
    Tila edellinen, nykyinen;
    std::chrono::nanoseconds kertyma{0};
    for (int ruutu = 0; ruutu < 90; ++ruutu) {  // 144 Hz:n näyttö
        kertyma += 1'000'000'000ns / 144;
        while (kertyma >= ASKEL) {
            edellinen = nykyinen;
            paivita(nykyinen, dt, true);
            kertyma -= ASKEL;
        }
        const double alfa = static_cast<double>(kertyma.count()) /
                            static_cast<double>(ASKEL.count());
        [[maybe_unused]] Tila piirra = sekoita(edellinen, nykyinen, alfa);
    }
    // @loppu kaytto
    std::println("x = {:.3f}, vx = {:.3f}", nykyinen.x, nykyinen.vx);
    std::println("limittäin: {}",
                 limittain({0, 0, 1, 1}, {1.5, 0.5, 1, 1}));
    Nappi hyppy;
    int hyppyja = 0;
    for (bool alhaalla : {false, true, true, false, true}) {
        hyppy.ruutu(alhaalla);
        hyppyja += hyppy.painettu();
    }
    std::println("hyppyjä {}", hyppyja);
}
