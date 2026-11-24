// Laaja vaihe: tasainen ruudukko karsii parit, joiden ei tarvitse
// testata törmäystä. Tulos on sama kuin kaikkien parien testauksella.
#include <cmath>
#include <cstdint>
#include <print>
#include <set>
#include <unordered_map>
#include <utility>
#include <vector>

struct Kappale {
    double x, y, r;
};

bool osuu(const Kappale& a, const Kappale& b) {
    const double dx = a.x - b.x, dy = a.y - b.y, r = a.r + b.r;
    return dx * dx + dy * dy < r * r;
}

using Parit = std::set<std::pair<int, int>>;

Parit kaikki_parit(const std::vector<Kappale>& k, long& testeja) {
    Parit tulos;
    for (int i = 0; i < static_cast<int>(k.size()); ++i) {
        for (int j = i + 1; j < static_cast<int>(k.size()); ++j) {
            ++testeja;
            if (osuu(k[i], k[j])) {
                tulos.insert({i, j});
            }
        }
    }
    return tulos;
}

// @alku ruudukko
// Solun koko vähintään suurimman kappaleen halkaisija: silloin
// törmäysparin kappaleet ovat samassa tai viereisessä solussa.
Parit ruudukko(const std::vector<Kappale>& k, double solu, long& testeja) {
    auto avain = [](int sx, int sy) {
        return (static_cast<std::int64_t>(sx) << 32) ^
               static_cast<std::uint32_t>(sy);
    };
    std::unordered_map<std::int64_t, std::vector<int>> solut;
    for (int i = 0; i < static_cast<int>(k.size()); ++i) {
        solut[avain(static_cast<int>(std::floor(k[i].x / solu)),
                    static_cast<int>(std::floor(k[i].y / solu)))]
            .push_back(i);
    }
    Parit tulos;
    for (int i = 0; i < static_cast<int>(k.size()); ++i) {
        const int sx = static_cast<int>(std::floor(k[i].x / solu));
        const int sy = static_cast<int>(std::floor(k[i].y / solu));
        for (int dy = -1; dy <= 1; ++dy) {
            for (int dx = -1; dx <= 1; ++dx) {
                auto it = solut.find(avain(sx + dx, sy + dy));
                if (it == solut.end()) {
                    continue;
                }
                for (int j : it->second) {
                    if (j > i) {  // jokainen pari vain kerran
                        ++testeja;
                        if (osuu(k[i], k[j])) {
                            tulos.insert({i, j});
                        }
                    }
                }
            }
        }
    }
    return tulos;
}
// @loppu ruudukko

int main() {
    // Toistettava "satunnainen" sijoittelu (lineaarinen kongruenssi).
    std::uint32_t tila = 12345;
    auto satunnainen = [&] {
        tila = tila * 1664525u + 1013904223u;
        return (tila >> 8) / static_cast<double>(1u << 24);
    };
    std::vector<Kappale> kappaleet;
    for (int i = 0; i < 2000; ++i) {
        kappaleet.push_back({satunnainen() * 1000.0, satunnainen() * 1000.0,
                             2.0 + satunnainen() * 6.0});
    }
    long testit_kaikki = 0, testit_ruudukko = 0;
    const Parit a = kaikki_parit(kappaleet, testit_kaikki);
    const Parit b = ruudukko(kappaleet, 16.0, testit_ruudukko);
    std::println("törmäyksiä {} / {}, samat: {}", a.size(), b.size(),
                 a == b);
    std::println("testejä: kaikki parit {}, ruudukko {}", testit_kaikki,
                 testit_ruudukko);
}
