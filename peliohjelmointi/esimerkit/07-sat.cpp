// Erottavan akselin lause (SAT) kuperille monikulmioille: kappaleet
// eivät leikkaa, jos jollekin särmän normaalille projisoidut välit
// ovat erillään.
#include <cmath>
#include <limits>
#include <numbers>
#include <optional>
#include <print>
#include <vector>

struct V2 {
    double x, y;
};
double piste(V2 a, V2 b) { return a.x * b.x + a.y * b.y; }

using Monikulmio = std::vector<V2>;  // kärjet vastapäivään

// @alku sat
struct Tulos {
    V2 normaali;   // suunta, johon a työnnetään irti b:stä
    double syvyys;
};

std::pair<double, double> projektio(const Monikulmio& m, V2 akseli) {
    double pienin = std::numeric_limits<double>::max(), suurin = -pienin;
    for (V2 p : m) {
        const double t = piste(p, akseli);
        pienin = std::min(pienin, t);
        suurin = std::max(suurin, t);
    }
    return {pienin, suurin};
}

std::optional<Tulos> sat(const Monikulmio& a, const Monikulmio& b) {
    Tulos paras{{0, 0}, std::numeric_limits<double>::max()};
    for (const Monikulmio* m : {&a, &b}) {
        for (std::size_t i = 0; i < m->size(); ++i) {
            const V2 p = (*m)[i], q = (*m)[(i + 1) % m->size()];
            V2 n{q.y - p.y, p.x - q.x};  // särmän ulkonormaali
            const double pit = std::hypot(n.x, n.y);
            n = {n.x / pit, n.y / pit};
            auto [a0, a1] = projektio(a, n);
            auto [b0, b1] = projektio(b, n);
            const double limitys = std::min(a1, b1) - std::max(a0, b0);
            if (limitys <= 0.0) {
                return std::nullopt;  // erottava akseli löytyi
            }
            if (limitys < paras.syvyys) {
                // Normaali osoittamaan b:stä poispäin a:n suuntaan.
                const bool kaanna = (a0 + a1) < (b0 + b1);
                paras = {kaanna ? V2{-n.x, -n.y} : n, limitys};
            }
        }
    }
    return paras;
}
// @loppu sat

Monikulmio laatikko(V2 keski, double puoli, double kulma) {
    Monikulmio m;
    for (int i = 0; i < 4; ++i) {
        const double k = kulma + std::numbers::pi / 4 +
                         i * std::numbers::pi / 2;
        const double r = puoli * std::numbers::sqrt2;
        m.push_back({keski.x + r * std::cos(k), keski.y + r * std::sin(k)});
    }
    return m;
}

int main() {
    const Monikulmio kolmio{{0, 0}, {4, 0}, {0, 4}};
    for (double x : {2.6, 2.4, 1.8}) {
        // Suoraan sijoitettu laatikko ja 45 astetta kierretty laatikko.
        for (double kulma : {0.0, std::numbers::pi / 4}) {
            const auto l = laatikko({x, x}, 0.5, kulma);
            const auto t = sat(l, kolmio);
            if (t) {
                std::println("keski ({:.1f}, {:.1f}), kulma {:2.0f}°: "
                             "syvyys {:.3f}, normaali ({:.2f}, {:.2f})",
                             x, x, kulma * 180 / std::numbers::pi,
                             t->syvyys, t->normaali.x, t->normaali.y);
            } else {
                std::println("keski ({:.1f}, {:.1f}), kulma {:2.0f}°: "
                             "erillään",
                             x, x, kulma * 180 / std::numbers::pi);
            }
        }
    }
}
