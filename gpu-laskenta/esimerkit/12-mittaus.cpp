// Suorituskyvyn mittaaminen aikaleimoilla: siirron hinta isännän ja
// laitteen muistin välillä sekä oman laitteen roofline-käyrä
// säädettävällä laskentaintensiteetillä. Testiajo tarkistaa vain
// aikaleimojen toiminnan ja tulosten oikeellisuuden; ajat tulostetaan
// valitsimella --mittaa.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <cmath>
#include <functional>
#include <vector>

struct Vakiot {
    std::uint32_t n, toistot;
};

// @alku mediaani
// Ajetaan toistot kertaa, ensimmäinen ajo on lämmittely. Tulos on
// mediaani nanosekunteina, koska yksittäiset ajot vaihtelevat.
double mittaa_ns(const VkYmparisto& vk, Ajastin& ajastin, int toistoja,
                 const std::function<void(VkCommandBuffer)>& komennot) {
    std::vector<double> ajat;
    for (int t = 0; t <= toistoja; ++t) {
        VkCommandBuffer kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        komennot(kp);
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        const double ns = ajastin.lue()[0];
        if (t > 0) ajat.push_back(ns);
    }
    std::ranges::sort(ajat);
    return ajat[ajat.size() / 2];
}
// @loppu mediaani

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    VkYmparisto vk;
    std::println("laskentajono tukee aikaleimoja: {} ({} bittia), "
                 "jakso {} ns", kylla(vk.aikaleimabitit > 0),
                 vk.aikaleimabitit, vk.ominaisuudet.limits.timestampPeriod);
    Ajastin ajastin(vk, 2);
    {
        VkCommandBuffer kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        std::println("aikaleimat kasvavat: {}", kylla(ajastin.lue()[0] >= 0));
    }

    // @alku siirto
    constexpr std::uint32_t n = 1u << 24;  // 64 MiB liukulukuja
    Puskuri<float> isanta(vk, n);          // CPU:lle näkyvä muisti
    Puskuri<float> laite(vk, n, true);     // laitteen oma muisti
    std::ranges::fill(isanta.alkiot(), 0.5f);
    const VkBufferCopy alue{0, 0, isanta.tavuja()};
    const double siirto_ns = mittaa_ns(vk, ajastin, 5, [&](auto kp) {
        vkCmdCopyBuffer(kp, isanta.puskuri, laite.puskuri, 1, &alue);
    });
    // @loppu siirto

    Putki kuorma(vk, "bin/kuorma.spv", 1, sizeof(Vakiot));
    const VkDescriptorSet j_laite = kuorma.joukko({laite.puskuri});
    const VkDescriptorSet j_isanta = kuorma.joukko({isanta.puskuri});
    if (mittaa) {
        std::println("siirto isanta -> laite: {:.1f} ms, {:.2f} Gt/s",
                     siirto_ns / 1e6,
                     static_cast<double>(isanta.tavuja()) / siirto_ns);
        std::println("{:>8} {:>10} {:>10} {:>10}", "toistot", "laskut/t",
                     "Glaskua/s", "Gt/s");
        // @alku roofline
        // Ryhmien määrä on enintään 65 535 suuntaa kohden
        // (maxComputeWorkGroupCount), joten ajetaan 2^22 säiettä.
        constexpr std::uint32_t m = 1u << 22;
        for (const std::uint32_t toistot : {1u, 4u, 16u, 64u, 256u}) {
            const double ns = mittaa_ns(vk, ajastin, 3, [&](auto kp) {
                kuorma.aja(kp, j_laite, Vakiot{m, toistot},
                           {ryhmia(m, 256)});
            });
            const double laskuja = 2.0 * toistot * m;
            std::println("{:>8} {:>10.2f} {:>10.2f} {:>10.2f}", toistot,
                         laskuja / (8.0 * m), laskuja / ns, 8.0 * m / ns);
        }
        // @loppu roofline
    }

    // Oikeellisuus: pieni ajo CPU:lle näkyvään muistiin, 256 toistoa.
    constexpr std::uint32_t m = 4096;
    std::ranges::generate(isanta.alkiot().first(m), [i = 0]() mutable {
        return static_cast<float>(i++ % 100) / 100.0f;
    });
    std::vector<float> odotettu(isanta.alkiot().begin(),
                                isanta.alkiot().begin() + m);
    for (float& x : odotettu) {
        for (int t = 0; t < 256; ++t) x = 0.999f * x + 0.001f;
    }
    VkCommandBuffer kp = vk.aloita();
    kuorma.aja(kp, j_isanta, Vakiot{m, 256}, {ryhmia(m, 256)});
    vk.suorita(kp);
    std::println("kuorman tulos sama kuin CPU:lla (ero < 1e-5): {}",
                 kylla(suurin_ero(isanta.alkiot().first(m), odotettu) <
                       1e-5));
    return Validointi::raportti();
}
