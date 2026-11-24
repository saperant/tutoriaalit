// Bloom-suodatin: joukko, joka voi vastata "ehkä" vaikka alkio puuttuu,
// mutta ei koskaan "ei", jos alkio on lisätty.
#include <cmath>
#include <cstdint>
#include <print>
#include <unordered_set>
#include <vector>

#include "testaus.hpp"

// @alku bloom
// Sekoitusfunktio (SplitMix64:n viimeistely): jokainen syötebitti
// vaikuttaa jokaiseen tulosbittiin.
static std::uint64_t sekoita(std::uint64_t z)
{
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9u;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBu;
    return z ^ (z >> 31);
}

class Bloom {
public:
    Bloom(std::size_t bitteja, int funktioita)
        : bitit_(bitteja, false), k_{funktioita}
    {
    }

    void lisaa(std::uint64_t avain)
    {
        for (int i = 0; i < k_; ++i) {
            bitit_[paikka(avain, i)] = true;
        }
    }

    bool ehka(std::uint64_t avain) const
    {
        for (int i = 0; i < k_; ++i) {
            if (!bitit_[paikka(avain, i)]) {
                return false;   // varmasti puuttuu
            }
        }
        return true;
    }

private:
    // Kaksoishajautus: k funktiota kahdesta hajautusarvosta,
    // h1 + i h2 (Kirsch ja Mitzenmacher 2006).
    std::size_t paikka(std::uint64_t avain, int i) const
    {
        std::uint64_t h1 = sekoita(avain);
        std::uint64_t h2 = sekoita(avain ^ 0x9E3779B97F4A7C15u) | 1;
        return (h1 + static_cast<std::uint64_t>(i) * h2) % bitit_.size();
    }

    std::vector<bool> bitit_;
    int k_;
};
// @loppu bloom

int main()
{
    // @alku mittaus
    // 10 bittiä alkiota kohden. Väärien positiivisten osuus mitataan
    // avaimilla, joita ei lisätty, ja sitä verrataan kaavaan
    // (1 - e^(-k n / m))^k.
    constexpr int n = 10000;
    constexpr std::size_t m = 10 * n;
    Satunnainen s{4};
    std::vector<std::uint64_t> lisatyt(n);
    std::unordered_set<std::uint64_t> malli;
    for (auto& x : lisatyt) {
        x = s.seuraava();
        malli.insert(x);
    }
    std::println("{:>2} {:>10} {:>10}", "k", "mitattu", "kaava");
    for (int k : {1, 2, 4, 7, 10, 14}) {
        Bloom suodatin{m, k};
        for (auto x : lisatyt) {
            suodatin.lisaa(x);
        }
        for (auto x : lisatyt) {
            vaadi(suodatin.ehka(x), "väärä negatiivinen");
        }
        int vaaria = 0, kokeita = 0;
        while (kokeita < 100000) {
            auto x = s.seuraava();
            if (!malli.contains(x)) {
                ++kokeita;
                vaaria += suodatin.ehka(x) ? 1 : 0;
            }
        }
        double kaava = std::pow(1 - std::exp(-1.0 * k * n / m), k);
        std::println("{:2} {:9.2f} % {:8.2f} %", k, 100.0 * vaaria / kokeita,
                     100 * kaava);
    }
    // @loppu mittaus
}
