// Bitoninen lajittelu: lajitteluverkko, jonka vertailut eivät riipu
// datasta. Ensin jokainen askel omana ajonaan, sitten lohkon sisäiset
// askeleet yhdessä ajossa jaetussa muistissa.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <bit>
#include <limits>
#include <vector>

struct Askel {
    std::uint32_t k, j;
};
struct Lohko {
    std::uint32_t k_alku, k_loppu, j_alku;
};

// @alku globaali
// Jokainen (k, j)-askel on oma ajonsa: työryhmät eivät voi odottaa
// toisiaan, joten globaalin askeleen jälkeen tarvitaan este.
int lajittele_globaalisti(VkCommandBuffer kp, const Putki& p,
                          VkDescriptorSet j, std::uint32_t n) {
    int ajoja = 0;
    for (std::uint32_t k = 2; k <= n; k *= 2) {
        for (std::uint32_t etaisyys = k / 2; etaisyys > 0; etaisyys /= 2) {
            p.aja(kp, j, Askel{k, etaisyys}, {n / 256});
            laskentaeste(kp);
            ++ajoja;
        }
    }
    return ajoja;
}
// @loppu globaali

// @alku yhdistelma
int lajittele_yhdistellen(VkCommandBuffer kp, const Putki& glob,
                          const Putki& lohko, VkDescriptorSet j,
                          std::uint32_t n) {
    // Ensin jokainen 512 alkion lohko kokonaan jaetussa muistissa.
    lohko.aja(kp, j, Lohko{2, 512, 256}, {n / 512});
    laskentaeste(kp);
    int ajoja = 1;
    for (std::uint32_t k = 1024; k <= n; k *= 2) {
        // Pitkät etäisyydet globaalisti, lyhyet yhdellä lohkoajolla.
        for (std::uint32_t e = k / 2; e >= 512; e /= 2) {
            glob.aja(kp, j, Askel{k, e}, {n / 256});
            laskentaeste(kp);
            ++ajoja;
        }
        lohko.aja(kp, j, Lohko{k, k, 256}, {n / 512});
        laskentaeste(kp);
        ++ajoja;
    }
    return ajoja;
}
// @loppu yhdistelma

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    // @alku taydennys
    // Verkko vaatii kahden potenssin: täydennetään suurimmalla arvolla,
    // jolloin täytteet päätyvät loppuun ja leikataan pois.
    constexpr std::uint32_t n = 200'000;
    constexpr std::uint32_t koko = std::bit_ceil(n);
    // @loppu taydennys
    VkYmparisto vk;
    Puskuri<std::uint32_t> data(vk, koko);
    Putki glob(vk, "bin/bitoninen.spv", 1, sizeof(Askel));
    Putki lohko(vk, "bin/bitoninen_jaettu.spv", 1, sizeof(Lohko));
    const VkDescriptorSet jg = glob.joukko({data.puskuri});
    const VkDescriptorSet jl = lohko.joukko({data.puskuri});
    Ajastin ajastin(vk, 2);

    Satunnainen s(7);
    std::vector<std::uint32_t> alkuperainen(n);
    std::ranges::generate(alkuperainen, [&] { return s.u32(); });
    auto odotettu = alkuperainen;
    std::ranges::sort(odotettu);
    std::println("alkioita {}, taydennetty kokoon {}", n, koko);
    std::println("{:12} {:>6} {:>12} {:>8}", "tapa", "ajoja", "vertailuja",
                 "oikein");
    for (const bool yhdistele : {false, true}) {
        std::ranges::copy(alkuperainen, data.alkiot().begin());
        std::ranges::fill(data.alkiot().subspan(n),
                          std::numeric_limits<std::uint32_t>::max());
        VkCommandBuffer kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        const int ajoja =
            yhdistele ? lajittele_yhdistellen(kp, glob, lohko, jl, koko)
                      : lajittele_globaalisti(kp, glob, jg, koko);
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        // Verkossa on log2(koko) * (log2(koko) + 1) / 2 askelta, ja
        // jokaisessa koko / 2 vertailua tavasta riippumatta.
        const auto l = static_cast<std::uint64_t>(std::bit_width(koko) - 1);
        std::println("{:12} {:>6} {:>12} {:>8}",
                     yhdistele ? "yhdistelma" : "globaali", ajoja,
                     l * (l + 1) / 2 * (koko / 2),
                     kylla(std::ranges::equal(data.alkiot().first(n),
                                              odotettu)));
        if (mittaa) {
            std::println("    aika {:.2f} ms", ajastin.lue()[0] / 1e6);
        }
    }
    return Validointi::raportti();
}
