// Interpolointi: 60 Hz:n simulaatio piirretään 144 Hz:n näytölle.
// Ilman interpolointia kappale nykii, koska osa ruuduista näyttää
// saman simulaatiotilan kahdesti.
#include <chrono>
#include <print>

using namespace std::chrono_literals;
using Kesto = std::chrono::nanoseconds;

constexpr Kesto ASKEL = 1'000'000'000ns / 60;
constexpr Kesto RUUTU = 1'000'000'000ns / 144;
constexpr double NOPEUS = 60.0;  // pikseliä sekunnissa

// @alku interpolointi
struct Tila {
    double x = 0.0;
};

Tila sekoita(const Tila& edellinen, const Tila& nykyinen, double alfa) {
    return {edellinen.x + (nykyinen.x - edellinen.x) * alfa};
}
// @loppu interpolointi

int main() {
    const double dt = std::chrono::duration<double>(ASKEL).count();
    Tila edellinen, nykyinen;
    Kesto kertyma{0};
    std::println("ruutu  ilman   interpoloitu");
    for (int ruutu = 1; ruutu <= 8; ++ruutu) {
        kertyma += RUUTU;
        while (kertyma >= ASKEL) {
            edellinen = nykyinen;
            nykyinen.x += NOPEUS * dt;
            kertyma -= ASKEL;
        }
        // @alku piirto
        const double alfa =
            static_cast<double>(kertyma.count()) / ASKEL.count();
        const Tila piirrettava = sekoita(edellinen, nykyinen, alfa);
        // @loppu piirto
        std::println("{:5} {:6.3f} {:10.3f}", ruutu, nykyinen.x,
                     piirrettava.x);
    }
}
