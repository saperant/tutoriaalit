// Histogrammi atomisilla operaatioilla: suoraan globaaliin muistiin ja
// yksityistettynä jaettuun muistiin. Kaksi dataa: tasainen ja vino,
// jossa lähes kaikki tavut ovat samoja (kilpailu yhdestä lokerosta).
#include "data.hpp"
#include "laskenta.hpp"

#include <array>
#include <vector>

struct Vakiot {
    std::uint32_t n;
};
struct JaetunVakiot {
    std::uint32_t n, sanoja_saikeelle;
};

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    constexpr std::uint32_t n = 1u << 22;  // sanoja, 4 tavua kussakin
    VkYmparisto vk;
    Puskuri<std::uint32_t> sanat(vk, n), lokerot(vk, 256), laskuri(vk, 1);
    Putki globaali(vk, "bin/histo_globaali.spv", 2, sizeof(Vakiot));
    Putki jaettu(vk, "bin/histo_jaettu.spv", 3, sizeof(JaetunVakiot));
    const VkDescriptorSet jg =
        globaali.joukko({sanat.puskuri, lokerot.puskuri});
    const VkDescriptorSet jj = jaettu.joukko(
        {sanat.puskuri, lokerot.puskuri, laskuri.puskuri});
    Ajastin ajastin(vk, 2);
    Satunnainen s(6);

    std::println("{:8} {:10} {:>12} {:>10}", "data", "tapa",
                 "globaaleja", "oikein");
    for (const bool vino : {false, true}) {
        for (std::uint32_t& sana : sanat.alkiot()) {
            sana = 0;
            for (int k = 0; k < 4; ++k) {
                // Vinossa datassa 15/16 tavuista on arvoa 32 (välilyönti).
                std::uint32_t t = s.u32() % 256;
                if (vino && s.u32() % 16 != 0) t = 32;
                sana |= t << (8 * k);
            }
        }
        std::array<std::uint32_t, 256> odotettu{};
        for (std::uint32_t sana : sanat.alkiot()) {
            for (int k = 0; k < 4; ++k) ++odotettu[(sana >> (8 * k)) & 0xFF];
        }
        // @alku ajot
        for (const int tapa : {0, 1}) {
            std::ranges::fill(lokerot.alkiot(), 0u);
            laskuri.alkiot()[0] = 0;
            VkCommandBuffer kp = vk.aloita();
            ajastin.merkitse(kp, 0);
            if (tapa == 0) {
                globaali.aja(kp, jg, Vakiot{n}, {ryhmia(n, 256)});
            } else {
                constexpr std::uint32_t sanoja = 16;
                jaettu.aja(kp, jj, JaetunVakiot{n, sanoja},
                           {ryhmia(n, 256 * sanoja)});
            }
            ajastin.merkitse(kp, 1);
            vk.suorita(kp);
            // @loppu ajot
            const double ns = ajastin.lue()[0];
            const std::uint64_t globaaleja =
                tapa == 0 ? 4ull * n : laskuri.alkiot()[0];
            std::println("{:8} {:10} {:>12} {:>10}",
                         vino ? "vino" : "tasainen",
                         tapa == 0 ? "globaali" : "jaettu", globaaleja,
                         kylla(std::ranges::equal(lokerot.alkiot(),
                                                  odotettu)));
            if (mittaa) {
                std::println("    aika {:.2f} ms", ns / 1e6);
            }
        }
    }
    return Validointi::raportti();
}
