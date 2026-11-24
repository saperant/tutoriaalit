// Törmäystestit yksinkertaisille muodoille ja erottava siirtymä
// (kuinka paljon ja mihin suuntaan kappaleet on työnnettävä erilleen).
#include <algorithm>
#include <cmath>
#include <optional>
#include <print>

struct V2 {
    double x, y;
    V2 operator-(V2 o) const { return {x - o.x, y - o.y}; }
    V2 operator+(V2 o) const { return {x + o.x, y + o.y}; }
    V2 operator*(double k) const { return {x * k, y * k}; }
};
double pituus(V2 v) { return std::hypot(v.x, v.y); }

// @alku aabb
struct Aabb {  // akselien suuntainen laatikko: keskipiste ja puolikoko
    V2 keski, puoli;
};

// Palauttaa siirtymän, jolla a työnnetään irti b:stä, tai ei mitään.
std::optional<V2> tormays(const Aabb& a, const Aabb& b) {
    const V2 d = b.keski - a.keski;
    const double px = (a.puoli.x + b.puoli.x) - std::abs(d.x);
    const double py = (a.puoli.y + b.puoli.y) - std::abs(d.y);
    if (px <= 0.0 || py <= 0.0) {
        return std::nullopt;  // erotteleva akseli löytyi
    }
    // Pienin päällekkäisyys kertoo lyhimmän ulospääsyn.
    if (px < py) {
        return V2{d.x < 0.0 ? px : -px, 0.0};
    }
    return V2{0.0, d.y < 0.0 ? py : -py};
}
// @loppu aabb

// @alku ympyra
struct Ympyra {
    V2 keski;
    double sade;
};

bool tormays(const Ympyra& a, const Ympyra& b) {
    const V2 d = b.keski - a.keski;
    const double r = a.sade + b.sade;
    return d.x * d.x + d.y * d.y < r * r;  // ei neliöjuurta
}

// Ympyrä ja laatikko: laatikon lähin piste ympyrän keskipisteeseen.
bool tormays(const Ympyra& y, const Aabb& b) {
    const V2 lahin{
        std::clamp(y.keski.x, b.keski.x - b.puoli.x, b.keski.x + b.puoli.x),
        std::clamp(y.keski.y, b.keski.y - b.puoli.y, b.keski.y + b.puoli.y)};
    const V2 d = y.keski - lahin;
    return d.x * d.x + d.y * d.y < y.sade * y.sade;
}
// @loppu ympyra

int main() {
    const Aabb seina{{0.0, 0.0}, {1.0, 3.0}};
    for (V2 paikka : {V2{2.5, 0.0}, V2{1.6, 0.5}, V2{0.2, 3.5}}) {
        const Aabb pelaaja{paikka, {1.0, 1.0}};
        if (auto s = tormays(pelaaja, seina)) {
            const V2 uusi = paikka + *s;
            std::println("pelaaja ({:.1f}, {:.1f}): törmää, siirretään "
                         "({:.1f}, {:.1f})", paikka.x, paikka.y, uusi.x,
                         uusi.y);
        } else {
            std::println("pelaaja ({:.1f}, {:.1f}): ei törmää", paikka.x,
                         paikka.y);
        }
    }
    const Ympyra pallo{{1.8, 3.8}, 1.0};
    std::println("pallo ja seinä: {}", tormays(pallo, seina));
    std::println("pallo ja pallo: {}",
                 tormays(pallo, Ympyra{{3.5, 3.8}, 1.0}));
    std::println("etäisyys {:.2f}", pituus(V2{3.5, 3.8} - pallo.keski));
}
