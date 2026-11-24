// Rakenteiden taulukko (AoS) vai taulukoiden rakenne (SoA) C++:lla.
#include <cstddef>
#include <ranges>
#include <string>
#include <string_view>
#include <tuple>
#include <vector>

#include "mittari.hpp"

// @alku aos
struct Hiukkanen {
    double x, y, z;
    double vx, vy, vz;
    double massa;
    std::string nimi;     // 32 tavua; yhteensä 88 tavua
};

[[gnu::noinline]] void siirra_aos(std::vector<Hiukkanen>& h, double dt)
{
    for (auto& p : h) {
        p.x += p.vx * dt;
    }
}
// @loppu aos

// @alku soa
// Sama tieto sarakkeina: x-päivitys lukee vain kahta tiivistä taulukkoa.
struct Hiukkaset {
    std::vector<double> x, y, z;
    std::vector<double> vx, vy, vz;
    std::vector<double> massa;
    std::vector<std::string> nimi;
};

[[gnu::noinline]] void siirra_soa(Hiukkaset& h, double dt)
{
    // zip-näkymä antaa rivikohtaisen kirjoitustavan sarakkeille.
    for (auto [x, vx] : std::views::zip(h.x, h.vx)) {
        x += vx * dt;
    }
}
// @loppu soa

struct Aineisto {
    std::vector<Hiukkanen> aos;
    Hiukkaset soa;
};

Aineisto luo(std::size_t n)
{
    Aineisto a;
    for (std::size_t i = 0; i < n; ++i) {
        double v = static_cast<double>(i % 17) - 8.0;
        a.aos.push_back({0, 0, 0, v, 0, 0, 1, "hiukkanen"});
        a.soa.x.push_back(0);
        a.soa.y.push_back(0);
        a.soa.z.push_back(0);
        a.soa.vx.push_back(v);
        a.soa.vy.push_back(0);
        a.soa.vz.push_back(0);
        a.soa.massa.push_back(1);
        a.soa.nimi.emplace_back("hiukkanen");
    }
    return a;
}

template <typename Toimi>
void valitse(std::string_view tapa, Aineisto& a, Toimi toimi)
{
    if (tapa == "aos") {
        toimi([&] { siirra_aos(a.aos, 0.01); });
    } else if (tapa == "soa") {
        toimi([&] { siirra_soa(a.soa, 0.01); });
    }
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    if (tila.mittaa) {
        auto a = luo(1'000'000);
        std::printf("x-paivitys, 1000000 hiukkasta\n");
        double vertailu = 0;
        for (std::string_view t : {"aos", "soa"}) {
            valitse(t, a, [&](auto f) {
                auto m = mittari::mittaa(f, 21);
                mittari::tulosta(t, m, vertailu);
                vertailu = m.mediaani_ms;
            });
        }
        return 0;
    }
    auto a = luo(10'000);
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, a, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    for (int k = 0; k < 100; ++k) {
        siirra_aos(a.aos, 0.01);
        siirra_soa(a.soa, 0.01);
    }
    double ero = 0;
    for (std::size_t i = 0; i < a.aos.size(); ++i) {
        ero += std::abs(a.aos[i].x - a.soa.x[i]);
    }
    std::printf("sizeof(Hiukkanen) = %zu\n", sizeof(Hiukkanen));
    std::printf("x[1] = %.2f, erot yhteensa %.2f\n", a.soa.x[1], ero);
}
