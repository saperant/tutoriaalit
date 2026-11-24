// Kaksiulotteinen ajo ja erikoistusvakiot: sama sumennusvarjostin
// eri työryhmän koolla ja säteellä. Tulos on kokonaislukuja, joten se
// vertaillaan CPU-referenssiin tarkasti.
#include "data.hpp"
#include "laskenta.hpp"

#include <vector>

struct Vakiot {
    std::uint32_t leveys;
    std::uint32_t korkeus;
};

// FNV-1a-tarkistussumma tuloksesta.
std::uint32_t tiiviste(std::span<const std::uint32_t> data) {
    std::uint32_t h = 2166136261u;
    for (std::uint32_t v : data) {
        h = (h ^ v) * 16777619u;
    }
    return h;
}

std::vector<std::uint32_t> sumenna_cpu(std::span<const std::uint32_t> k,
                                       int l, int h, int r) {
    std::vector<std::uint32_t> tulos(k.size());
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < l; ++x) {
            std::uint32_t summa = 0, maara = 0;
            for (int dy = -r; dy <= r; ++dy) {
                for (int dx = -r; dx <= r; ++dx) {
                    const int qx = x + dx, qy = y + dy;
                    if (qx >= 0 && qy >= 0 && qx < l && qy < h) {
                        summa += k[static_cast<std::size_t>(qy * l + qx)];
                        ++maara;
                    }
                }
            }
            tulos[static_cast<std::size_t>(y * l + x)] =
                (summa + maara / 2) / maara;
        }
    }
    return tulos;
}

int main() {
    constexpr std::uint32_t L = 1000, K = 750;
    VkYmparisto vk;
    Puskuri<std::uint32_t> lahde(vk, L * K), kohde(vk, L * K);
    Satunnainen s(2);
    for (std::uint32_t y = 0; y < K; ++y) {
        for (std::uint32_t x = 0; x < L; ++x) {
            // Liukuväri ja kohinaa, arvot 0...255.
            lahde.alkiot()[y * L + x] = (x * 255 / L + s.u32() % 32) % 256;
        }
    }
    std::println("raja: enintaan {} saietta tyoryhmassa",
                 vk.ominaisuudet.limits.maxComputeWorkGroupInvocations);

    std::println("{:12}  {:>4}  {:11}  {:8}  {}", "ryhman koko", "sade",
                 "ryhmia", "tiiviste", "sama kuin CPU");
    // @alku kokoonpanot
    struct Kokoonpano {
        std::uint32_t lx, ly;
        int sade;
    };
    for (const Kokoonpano k : {Kokoonpano{8, 8, 1}, {16, 16, 1},
                               {32, 8, 1}, {256, 1, 1}, {16, 16, 3}}) {
        Putki putki(vk, "bin/sumennus.spv", 2, sizeof(Vakiot),
                    {{0, k.lx}, {1, k.ly},
                     {2, static_cast<std::uint32_t>(k.sade)}});
        const VkDescriptorSet j =
            putki.joukko({lahde.puskuri, kohde.puskuri});
        const std::uint32_t gx = ryhmia(L, k.lx), gy = ryhmia(K, k.ly);
        VkCommandBuffer kp = vk.aloita();
        putki.aja(kp, j, Vakiot{L, K}, {gx, gy});
        vk.suorita(kp);
        // @loppu kokoonpanot
        const auto odotettu = sumenna_cpu(lahde.alkiot(), L, K, k.sade);
        std::println("{:5} x {:<4}  {:4}  {:4} x {:<4}  {:08x}  {}",
                     k.lx, k.ly, k.sade, gx, gy, tiiviste(kohde.alkiot()),
                     kylla(eroavia<std::uint32_t>(kohde.alkiot(),
                                                  odotettu) == 0));
    }
    return Validointi::raportti();
}
