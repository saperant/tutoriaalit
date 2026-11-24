// Matriisitulo suoraan ja laatoittain jaetun muistin kautta. Tulosta
// verrataan kaksoistarkkuudella laskettuun viitteeseen, ja muistihakujen
// määrästä lasketaan laskentaintensiteetti roofline-mallia varten.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <vector>

struct Vakiot {
    std::uint32_t M, N, K;
};

// @alku intensiteetti
// Jokainen C:n alkio vaatii K kertolaskua ja K yhteenlaskua. Suora
// tapa lataa 2K lukua (4 tavua kukin) globaalista muistista, laatoitus
// 2K / 16, koska jokainen ladattu luku käytetään 16 säikeessä.
struct Malli {
    double latauksia, intensiteetti;  // lukuja alkiota kohden, laskut/t
};

Malli mallinna(int tapa, std::uint32_t K) {
    const double latauksia = tapa == 0 ? 2.0 * K : 2.0 * K / 16;
    return {latauksia, 2.0 * K / (latauksia * 4)};
}
// @loppu intensiteetti

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    constexpr std::uint32_t M = 300, N = 260, K = 280;
    VkYmparisto vk;
    Puskuri<float> a(vk, M * K), b(vk, K * N), c(vk, M * N);
    Satunnainen s(10);
    std::ranges::generate(a.alkiot(), [&] { return s.f32() - 0.5f; });
    std::ranges::generate(b.alkiot(), [&] { return s.f32() - 0.5f; });
    std::vector<float> odotettu(M * N);
    for (std::uint32_t i = 0; i < M; ++i) {
        for (std::uint32_t j = 0; j < N; ++j) {
            double summa = 0.0;
            for (std::uint32_t k = 0; k < K; ++k) {
                summa += static_cast<double>(a.alkiot()[i * K + k]) *
                         b.alkiot()[k * N + j];
            }
            odotettu[i * N + j] = static_cast<float>(summa);
        }
    }
    Ajastin ajastin(vk, 2);
    std::println("C ({} x {}) = A ({} x {}) B ({} x {})", M, N, M, K, K, N);
    std::println("{:8} {:>14} {:>14} {:>12}", "tapa", "latauksia/alkio",
                 "laskut/tavu", "ero < 1e-5");
    for (const int tapa : {0, 1}) {
        const Malli m = mallinna(tapa, K);
        Putki putki(vk, tapa == 0 ? "bin/matmul_suora.spv"
                                  : "bin/matmul_laatta.spv",
                    3, sizeof(Vakiot));
        const VkDescriptorSet j =
            putki.joukko({a.puskuri, b.puskuri, c.puskuri});
        std::ranges::fill(c.alkiot(), 0.0f);
        VkCommandBuffer kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        putki.aja(kp, j, Vakiot{M, N, K}, {ryhmia(N, 16), ryhmia(M, 16)});
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        std::println("{:8} {:>14.1f} {:>14.2f} {:>12}",
                     tapa == 0 ? "suora" : "laatta", m.latauksia,
                     m.intensiteetti,
                     kylla(suurin_ero(c.alkiot(), odotettu) < 1e-5));
        if (mittaa) {
            const double ns = ajastin.lue()[0];
            std::println("    aika {:.2f} ms, {:.2f} Glaskua/s", ns / 1e6,
                         2.0 * M * N * K / ns);
        }
    }
    return Validointi::raportti();
}
