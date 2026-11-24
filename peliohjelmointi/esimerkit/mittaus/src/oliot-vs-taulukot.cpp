// Mittaus: oliohierarkia (virtuaalikutsu, oliot hajallaan keossa)
// vastaan tiiviit taulukot (ECS:n tapaan). Käännetään optimoiden
// (-O2), ja tuloste on pelkkä vertailu, jotta se on toistettava.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <memory>
#include <numeric>
#include <print>
#include <random>
#include <vector>

constexpr std::size_t N = 1u << 20;  // noin miljoona oliota

// @alku oliot
struct Olio {
    virtual ~Olio() = default;
    virtual void paivita(double dt) = 0;
    double x = 0.0, vx = 1.0;
    char muu_data[48]{};  // nimi, tila ym., joita päivitys ei tarvitse
};
struct Liikkuva final : Olio {
    void paivita(double dt) override { x += vx * dt; }
};
// @loppu oliot

// @alku taulukot
struct Liikkuvat {  // taulukoiden rakenne: vain tarvittavat kentät
    std::vector<double> x, vx;
    void paivita(double dt) {
        for (std::size_t i = 0; i < x.size(); ++i) {
            x[i] += vx[i] * dt;  // peräkkäinen muisti, vektoroituu
        }
    }
};
// @loppu taulukot

template <typename F>
double paras_aika(F&& f) {
    double paras = 1e9;
    for (int kierros = 0; kierros < 5; ++kierros) {
        const auto alku = std::chrono::steady_clock::now();
        for (int i = 0; i < 10; ++i) {
            f();
        }
        const std::chrono::duration<double> kesto =
            std::chrono::steady_clock::now() - alku;
        paras = std::min(paras, kesto.count());
    }
    return paras;
}

int main() {
    // Oliot varataan erikseen ja järjestys sekoitetaan: pitkään
    // pyörineessä pelissä keko on pirstoutunut samalla tavalla.
    std::vector<std::unique_ptr<Olio>> oliot;
    for (std::size_t i = 0; i < N; ++i) {
        oliot.push_back(std::make_unique<Liikkuva>());
    }
    std::shuffle(oliot.begin(), oliot.end(), std::mt19937(1));
    Liikkuvat taulukot{std::vector<double>(N, 0.0),
                       std::vector<double>(N, 1.0)};

    const double t_oliot = paras_aika([&] {
        for (auto& o : oliot) {
            o->paivita(1.0 / 60.0);
        }
    });
    const double t_taulukot =
        paras_aika([&] { taulukot.paivita(1.0 / 60.0); });
    const double summa = std::accumulate(
        taulukot.x.begin(), taulukot.x.end(), 0.0);
    std::println("tulokset samat: {}",
                 std::abs(summa - oliot.front()->x * N) < 1e-3 * N);
    std::println("taulukot vähintään 2 kertaa nopeampia: {}",
                 t_oliot > 2.0 * t_taulukot ? "kyllä" : "ei");
    std::fprintf(stderr, "oliot %.1f ms, taulukot %.1f ms (%.1fx)\n",
                 t_oliot * 100, t_taulukot * 100, t_oliot / t_taulukot);
}
