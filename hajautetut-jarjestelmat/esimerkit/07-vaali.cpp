// Raftin johtajavaali viidellä palvelimella: ensimmäinen vaali,
// uusi vaali johtajan kaaduttua ja satunnaistetun aikarajan merkitys.
#include <cstdio>
#include <memory>

#include "yhteinen/raft.hpp"

constexpr int N = 5;

// @alku kokoonpano
struct Raft {
    Tarkkailija tark;
    Simulaattori<RaftViesti, RaftLevy> sim;

    Raft(std::uint64_t siemen, Aika vmin, Aika vmax)
        : sim(N, siemen, {.viive_min = 1, .viive_max = 10},
              [this, vmin, vmax](int, RaftLevy& levy) {
                  return std::make_unique<RaftSolmu>(N, levy, tark, vmin,
                                                     vmax);
              }) {}

    // Johtaja, jonka termi on suurin, tai -1.
    int johtaja() {
        int paras = -1, termi = -1;
        for (int i = 0; i < N; ++i) {
            auto* s = sim.solmu<RaftSolmu>(i);
            if (s && s->rooli() == RaftSolmu::Rooli::Johtaja &&
                s->termi() > termi) {
                paras = i;
                termi = s->termi();
            }
        }
        return paras;
    }

    // Aika, jona johtaja löytyy, tai -1 aikarajaan mennessä.
    Aika odota_johtajaa(Aika asti) {
        for (Aika t = sim.nyt() + 1; t <= asti; ++t) {
            sim.aja(t);
            if (johtaja() >= 0) return t;
        }
        return -1;
    }
};
// @loppu kokoonpano

int main() {
    // @alku jalki
    {
        Raft r(3, 150, 300);
        r.sim.tulosta_loki(true);
        r.odota_johtajaa(1000);
        int j = r.johtaja();
        r.sim.aja(1000);
        r.sim.kaada(j);
        r.odota_johtajaa(2000);
    }
    // @loppu jalki

    // @alku tilasto
    std::printf("\naikaraja      ensimmainen vaali    uusi vaali kaatumisen "
                "jalkeen\n");
    std::printf("              ka. ms   termeja     ka. ms   ei johtajaa\n");
    for (auto [vmin, vmax] : {std::pair<Aika, Aika>{150, 300},
                              {150, 160}, {150, 150}}) {
        Aika eka = 0, uusi = 0;
        int termeja = 0, epaonnistui = 0, lkm = 0, rikkeet = 0;
        for (std::uint64_t s = 1; s <= 100; ++s) {
            Raft r(s, vmin, vmax);
            Aika t = r.odota_johtajaa(5000);
            if (t < 0) {
                ++epaonnistui;
                continue;
            }
            eka += t;
            termeja += r.sim.solmu<RaftSolmu>(r.johtaja())->termi();
            r.sim.aja(1000);
            r.sim.kaada(r.johtaja());
            Aika t2 = r.odota_johtajaa(6000);
            if (t2 < 0) ++epaonnistui;
            else uusi += t2 - 1000;
            ++lkm;
            if (!r.tark.ensimmainen.empty()) ++rikkeet;
        }
        std::printf("%3lld-%-3lld ms  ", static_cast<long long>(vmin),
                    static_cast<long long>(vmax));
        if (lkm == 0)
            std::printf("     -         -          -");
        else
            std::printf("%6lld  %8.2f  %9lld", static_cast<long long>(
                            eka / lkm),
                        static_cast<double>(termeja) / lkm,
                        static_cast<long long>(uusi / lkm));
        std::printf("  %12d\n", epaonnistui);
        if (rikkeet) std::printf("TURVALLISUUSRIKE %d ajossa\n", rikkeet);
    }
    // @loppu tilasto
}
