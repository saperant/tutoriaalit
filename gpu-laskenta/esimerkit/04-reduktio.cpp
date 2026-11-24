// Reduktio (summa) kolmella tavalla: atomisesti, puuna jaetussa
// muistissa ja aliryhmäoperaatioilla. Lopuksi liukulukusumman tarkkuus
// puuna ja peräkkäin laskettuna.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <cmath>
#include <memory>
#include <numeric>
#include <vector>

struct Vakiot {
    std::uint32_t n;
};

// @alku monivaihe
// Monivaiheinen reduktio: jokainen ajo pienentää datan 512-osaan.
// Työryhmät eivät voi odottaa toisiaan saman ajon sisällä, joten
// vaiheiden välissä on ajojen välinen este.
template <typename T>
T summaa(const VkYmparisto& vk, Putki& putki, Puskuri<T>& syote,
         int& ajoja, Ajastin* ajastin = nullptr) {
    std::vector<std::unique_ptr<Puskuri<T>>> osat;
    VkCommandBuffer kp = vk.aloita();
    if (ajastin) ajastin->merkitse(kp, 0);
    Puskuri<T>* lahde = &syote;
    std::size_t n = syote.koko();
    ajoja = 0;
    while (n > 1) {
        const std::uint32_t r = ryhmia(n, 512);
        osat.push_back(std::make_unique<Puskuri<T>>(vk, r));
        const VkDescriptorSet j =
            putki.joukko({lahde->puskuri, osat.back()->puskuri});
        putki.aja(kp, j, Vakiot{static_cast<std::uint32_t>(n)}, {r});
        laskentaeste(kp);
        lahde = osat.back().get();
        n = r;
        ++ajoja;
    }
    if (ajastin) ajastin->merkitse(kp, 1);
    vk.suorita(kp);
    return lahde->alkiot()[0];
}
// @loppu monivaihe

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    constexpr std::uint32_t n = (1u << 22) + 12345;
    VkYmparisto vk;
    Puskuri<std::uint32_t> x(vk, n), summa(vk, 1);
    Satunnainen s(4);
    std::ranges::generate(x.alkiot(), [&] { return s.u32() % 256; });
    const std::uint64_t odotettu = std::accumulate(
        x.alkiot().begin(), x.alkiot().end(), std::uint64_t{0});
    std::println("alkioita {}, summa {}", n, odotettu);
    std::println("{:10} {:>6} {:>12} {:>8}", "tapa", "ajoja",
                 "atomisia", "oikein");
    Ajastin ajastin(vk, 2);

    // @alku atomi
    Putki atomi(vk, "bin/reduktio_atomi.spv", 2, sizeof(Vakiot));
    summa.alkiot()[0] = 0;
    VkCommandBuffer kp = vk.aloita();
    ajastin.merkitse(kp, 0);
    atomi.aja(kp, atomi.joukko({x.puskuri, summa.puskuri}), Vakiot{n},
              {ryhmia(n, 256)});
    ajastin.merkitse(kp, 1);
    vk.suorita(kp);
    // @loppu atomi
    std::println("{:10} {:>6} {:>12} {:>8}", "atomi", 1, n,
                 kylla(summa.alkiot()[0] == odotettu));
    const double t_atomi = ajastin.lue()[0];

    double t[2];
    const char* nimet[] = {"jaettu", "aliryhma"};
    const char* varjostimet[] = {"bin/reduktio_jaettu.spv",
                                 "bin/reduktio_aliryhma.spv"};
    for (int k = 0; k < 2; ++k) {
        Putki putki(vk, varjostimet[k], 2, sizeof(Vakiot));
        int ajoja = 0;
        const std::uint32_t tulos = summaa(vk, putki, x, ajoja, &ajastin);
        t[k] = ajastin.lue()[0];
        std::println("{:10} {:>6} {:>12} {:>8}", nimet[k], ajoja, 0,
                     kylla(tulos == odotettu));
    }

    // @alku liukuluku
    constexpr std::uint32_t m = 1u << 22;
    Puskuri<float> f(vk, m);
    std::ranges::generate(f.alkiot(), [&] { return s.f32(); });
    double viite = 0.0;     // tarkka viite kaksoistarkkuudella
    float perakkain = 0.0f; // tavallinen silmukka floatilla
    for (float v : f.alkiot()) {
        viite += v;
        perakkain += v;
    }
    Putki puu(vk, "bin/reduktio_float.spv", 2, sizeof(Vakiot));
    int ajoja = 0;
    const float gpu = summaa(vk, puu, f, ajoja);
    const double virhe_perakkain = std::abs(perakkain - viite) / viite;
    const double virhe_puu = std::abs(gpu - viite) / viite;
    // @loppu liukuluku
    std::println("\nfloat-summa, {} alkiota:", m);
    std::println("perakkain: suhteellinen virhe alle 1e-3: {}, "
                 "alle 1e-5: {}", kylla(virhe_perakkain < 1e-3),
                 kylla(virhe_perakkain < 1e-5));
    std::println("puuna GPU:lla: suhteellinen virhe alle 1e-6: {}",
                 kylla(virhe_puu < 1e-6));

    if (mittaa) {
        std::println("aika atomi {:.2f} ms, jaettu {:.2f} ms, "
                     "aliryhma {:.2f} ms", t_atomi / 1e6, t[0] / 1e6,
                     t[1] / 1e6);
        std::println("virhe perakkain {:.2e}, puu {:.2e}",
                     virhe_perakkain, virhe_puu);
    }
    return Validointi::raportti();
}
