// Integraattorien vertailu jousella: energian pitäisi säilyä, mutta
// eksplisiittinen Euler lisää sitä, ja jousi "räjähtää".
#include <print>

constexpr double K = 40.0;  // jousivakio
constexpr double M = 1.0;   // massa

double kiihtyvyys(double x) { return -K / M * x; }

double energia(double x, double v) {
    return 0.5 * M * v * v + 0.5 * K * x * x;
}

// @alku integraattorit
struct Tila {
    double x, v;
};

// Eksplisiittinen Euler: paikka ja nopeus vanhoilla arvoilla.
void euler(Tila& s, double dt) {
    const double a = kiihtyvyys(s.x);
    s.x += s.v * dt;
    s.v += a * dt;
}

// Semi-implisiittinen (symplektinen) Euler: ensin nopeus, sitten
// paikka uudella nopeudella. Yhtä halpa, mutta energia ei karkaa.
void semi_implisiittinen(Tila& s, double dt) {
    s.v += kiihtyvyys(s.x) * dt;
    s.x += s.v * dt;
}

// Nopeus-Verlet: toisen kertaluvun tarkkuus, kiihtyvyys kahdesti.
void verlet(Tila& s, double dt) {
    const double a0 = kiihtyvyys(s.x);
    s.x += s.v * dt + 0.5 * a0 * dt * dt;
    const double a1 = kiihtyvyys(s.x);
    s.v += 0.5 * (a0 + a1) * dt;
}
// @loppu integraattorit

int main() {
    constexpr double dt = 1.0 / 30.0;
    const double alku = energia(1.0, 0.0);
    std::println("energia / alkuenergia 10 s:n jälkeen (dt = 1/30 s):");
    for (auto [nimi, askel] :
         {std::pair{"Euler", &euler},
          std::pair{"semi-implisiittinen", &semi_implisiittinen},
          std::pair{"Verlet", &verlet}}) {
        Tila s{1.0, 0.0};
        double suurin = 0.0;
        for (int i = 0; i < 300; ++i) {
            askel(s, dt);
            suurin = std::max(suurin, energia(s.x, s.v) / alku);
        }
        std::println("  {:20} lopussa {:8.3f}, suurin {:8.3f}", nimi,
                     energia(s.x, s.v) / alku, suurin);
    }
}
