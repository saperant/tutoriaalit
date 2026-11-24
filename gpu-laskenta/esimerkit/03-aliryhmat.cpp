// Aliryhmät lavapipellä ja malli muille leveyksille: kuinka moni
// aliryhmä hajaantuu eri haarautumisehdoilla. Lopuksi käyttöasteen
// (occupancy) laskuri esimerkkilaitteelle.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <array>

struct Tulos {
    std::uint32_t koko, aliryhmia, jarjestysvirheet, summavirheet;
    std::array<std::uint32_t, 4> hajaantuneet;
};

bool ehto(int kuvio, std::uint32_t i) {
    switch (kuvio) {
    case 0: return (i / 64) % 2 == 0;
    case 1: return i % 16 < 8;
    case 2: return i % 2 == 0;
    default: return i % 256 != 7;
    }
}

// @alku malli
// CPU-malli: n säiettä jaetaan leveyden w aliryhmiin, ja lasketaan,
// monessako ehto on osalle tosi ja osalle epätosi.
std::uint32_t hajaantuneita(int kuvio, std::uint32_t n, std::uint32_t w) {
    std::uint32_t maara = 0;
    for (std::uint32_t alku = 0; alku < n; alku += w) {
        std::uint32_t tosia = 0;
        for (std::uint32_t i = alku; i < alku + w; ++i) {
            tosia += ehto(kuvio, i) ? 1 : 0;
        }
        maara += (tosia != 0 && tosia != w) ? 1 : 0;
    }
    return maara;
}
// @loppu malli

// @alku kayttoaste
// Käyttöaste esimerkkilaitteella, jonka laskentayksikössä on 65 536
// rekisteriä, 64 KiB jaettua muistia ja tilaa 48 aallolle (32 kaistaa)
// sekä 16 työryhmälle. Raja tulee siitä resurssista, joka loppuu ensin.
struct Ytimen_tarve {
    std::uint32_t ryhman_koko, rekistereita, jaettua_tavua;
};

std::uint32_t ryhmia_kerralla(const Ytimen_tarve& t) {
    const std::uint32_t aaltoja = (t.ryhman_koko + 31) / 32;
    const std::uint32_t rajat[] = {
        65536 / (t.rekistereita * aaltoja * 32),   // rekisterit
        t.jaettua_tavua ? 65536 / t.jaettua_tavua  // jaettu muisti
                        : 16u,
        48 / aaltoja,                              // aaltopaikat
        16};                                       // työryhmäpaikat
    return std::ranges::min(rajat);
}
// @loppu kayttoaste

int main() {
    constexpr std::uint32_t n = 65536;
    VkYmparisto vk;
    Puskuri<Tulos> tulos(vk, 1);
    tulos.alkiot()[0] = {};
    Putki putki(vk, "bin/aliryhmat.spv", 1);
    const VkDescriptorSet j = putki.joukko({tulos.puskuri});
    VkCommandBuffer kp = vk.aloita();
    putki.aja(kp, j, {n / 256});
    vk.suorita(kp);

    const Tulos& t = tulos.alkiot()[0];
    std::println("aliryhman koko {}, aliryhmia tyoryhmassa {}", t.koko,
                 t.aliryhmia);
    std::println("aliryhmat ovat perakkaisia saikeita: {}",
                 kylla(t.jarjestysvirheet == 0));
    std::println("subgroupAdd laski oikein: {}", kylla(t.summavirheet == 0));

    const char* nimet[] = {"(i / 64) % 2 == 0", "i % 16 < 8",
                           "i % 2 == 0", "i % 256 != 7"};
    std::println("\nhajaantuneet aliryhmat ({} saietta):", n);
    std::println("{:18} {:>9} {:>8} {:>8} {:>8}", "ehto", "GPU (8)",
                 "malli 8", "malli 32", "malli 64");
    bool samat = true;
    for (int k = 0; k < 4; ++k) {
        const auto ku = static_cast<std::size_t>(k);
        samat = samat && t.hajaantuneet[ku] == hajaantuneita(k, n, t.koko);
        std::println("{:18} {:>9} {:>8} {:>8} {:>8}", nimet[ku],
                     t.hajaantuneet[ku], hajaantuneita(k, n, 8),
                     hajaantuneita(k, n, 32), hajaantuneita(k, n, 64));
    }
    std::println("GPU vastaa mallia: {}", kylla(samat));

    std::println("\nkayttoaste esimerkkilaitteella (enintaan 48 aaltoa):");
    std::println("{:>6} {:>10} {:>12} {:>8} {:>7} {:>7}", "ryhma",
                 "rek/saie", "jaettu (t)", "ryhmia", "aaltoja", "aste");
    for (const Ytimen_tarve y : {Ytimen_tarve{256, 32, 0},
                                 {256, 64, 0}, {256, 32, 16384},
                                 {1024, 32, 0}, {64, 128, 4096}}) {
        const std::uint32_t r = ryhmia_kerralla(y);
        const std::uint32_t aallot = r * ((y.ryhman_koko + 31) / 32);
        std::println("{:>6} {:>10} {:>12} {:>8} {:>7} {:>6}%",
                     y.ryhman_koko, y.rekistereita, y.jaettua_tavua, r,
                     aallot, aallot * 100 / 48);
    }
    return Validointi::raportti();
}
