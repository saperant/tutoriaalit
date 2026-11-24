// SAXPY (y = a*x + y) laskentavarjostimella: puskurit, push-vakiot,
// työryhmien määrä ja tuloksen vertailu CPU-referenssiin.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <vector>

// @alku vakiot
// Sama asettelu kuin varjostimen push_constant-lohkossa (std430).
struct Vakiot {
    std::uint32_t n;
    float a;
};
static_assert(sizeof(Vakiot) == 8);
// @loppu vakiot

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    // @alku ajo
    constexpr std::uint32_t ryhman_koko = 256;  // = local_size_x
    constexpr std::uint32_t n = 1'000'003;      // ei ryhmän monikerta
    constexpr float a = 2.5f;

    VkYmparisto vk;
    Puskuri<float> x(vk, n), y(vk, n);
    Satunnainen s(1);
    std::ranges::generate(x.alkiot(), [&] { return s.f32(); });
    std::ranges::generate(y.alkiot(), [&] { return s.f32(); });
    std::vector<float> odotettu(n);
    for (std::size_t i = 0; i < n; ++i) {
        odotettu[i] = a * x.alkiot()[i] + y.alkiot()[i];
    }

    Putki saxpy(vk, "bin/saxpy.spv", 2, sizeof(Vakiot));
    const VkDescriptorSet j = saxpy.joukko({x.puskuri, y.puskuri});
    const std::uint32_t ryhmat = ryhmia(n, ryhman_koko);

    VkCommandBuffer kp = vk.aloita();
    saxpy.aja(kp, j, Vakiot{n, a}, {ryhmat});
    vk.suorita(kp);
    // @loppu ajo

    std::println("alkioita {}, tyoryhmia {} x {} = {} saietta "
                 "({} ylimaaraista)",
                 n, ryhmat, ryhman_koko, ryhmat * ryhman_koko,
                 ryhmat * ryhman_koko - n);
    const double ero = suurin_ero(y.alkiot(), odotettu);
    std::println("suurin suhteellinen ero CPU:hun alle 1e-6: {}",
                 kylla(ero < 1e-6));

    // @alku vaarin
    // Yleinen virhe: ryhmien määrä pyöristetään alaspäin.
    std::ranges::fill(y.alkiot(), 0.0f);
    kp = vk.aloita();
    saxpy.aja(kp, j, Vakiot{n, 1.0f}, {n / ryhman_koko});
    vk.suorita(kp);
    const auto laskematta = std::ranges::count(y.alkiot(), 0.0f);
    std::println("ryhmat n / {} = {}: laskematta jai {} alkiota",
                 ryhman_koko, n / ryhman_koko, laskematta);
    // @loppu vaarin

    if (mittaa) {
        Ajastin ajastin(vk, 2);
        kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        saxpy.aja(kp, j, Vakiot{n, a}, {ryhmat});
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        const double ns = ajastin.lue()[0];
        std::println("aika {:.3f} ms, {:.2f} Gt/s", ns / 1e6,
                     12.0 * n / ns);
    }
    return Validointi::raportti();
}
