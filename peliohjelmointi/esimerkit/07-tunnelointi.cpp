// Tunneloituminen: nopea ammus hyppää ohuen seinän yli, koska törmäys
// tarkistetaan vain askelten lopuissa. Pyyhkäisytesti löytää osuman.
#include <algorithm>
#include <limits>
#include <optional>
#include <print>

struct Seina {
    double vasen, oikea;  // x-väli, seinä on pystysuora
};

bool sisalla(double x, const Seina& s) {
    return x >= s.vasen && x <= s.oikea;
}

// @alku pyyhkaisy
// Liikkeen jana x0 -> x0 + dx leikataan seinän väliin. Palauttaa osuman
// ajan murto-osana askeleesta (0..1).
std::optional<double> pyyhkaisy(double x0, double dx, const Seina& s) {
    if (dx == 0.0) {
        return sisalla(x0, s) ? std::optional{0.0} : std::nullopt;
    }
    double t0 = (s.vasen - x0) / dx;
    double t1 = (s.oikea - x0) / dx;
    if (t0 > t1) {
        std::swap(t0, t1);
    }
    if (t1 < 0.0 || t0 > 1.0) {
        return std::nullopt;
    }
    return std::max(t0, 0.0);
}
// @loppu pyyhkaisy

int main() {
    const Seina seina{10.0, 10.2};
    constexpr double dt = 1.0 / 60.0;
    for (double nopeus : {60.0, 420.0, 900.0}) {
        // @alku diskreetti
        double x = 0.0;
        bool osui = false;
        for (int i = 0; i < 120 && !osui; ++i) {
            x += nopeus * dt;
            osui = sisalla(x, seina);  // vain askeleen lopussa
        }
        // @loppu diskreetti
        x = 0.0;
        std::optional<double> osuma;
        int askel = 0;
        for (; askel < 120 && !osuma; ++askel) {
            osuma = pyyhkaisy(x, nopeus * dt, seina);
            if (!osuma) {
                x += nopeus * dt;
            }
        }
        std::println("{:4.0f} m/s: askeleen lopussa {}, pyyhkäisy {}",
                     nopeus, osui ? "osuu" : "ohi",
                     osuma ? "osuu" : "ohi");
    }
}
