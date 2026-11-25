// Matriisin transpoosi: suora, laatoitettu ja laatoitettu täytteellä.
// Lavapipe ei paljasta muistihakujen hintaa, joten varjostimien
// osoitteet lasketaan myös mallilla: montako 128 tavun segmenttiä
// 32 säikeen aalto koskee ja kuinka monta kertaa jaetun muistin pankki
// on varattu (pankkikonflikti).
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <functional>
#include <set>
#include <vector>

struct Vakiot {
    std::uint32_t leveys, korkeus;
};

constexpr std::uint32_t L = 1000, K = 760;  // ei 32:n monikertoja

// @alku malli
// Yksi muistikäsky 32 kaistan aallossa: kaista -> sanan osoite tai -1,
// jos kaista ei ole mukana (matriisin reunan yli).
using Osoite = std::function<long(std::uint32_t kaista)>;

// Globaali muisti: montako eri 128 tavun segmenttiä käsky koskee.
std::size_t segmentteja(const Osoite& osoite) {
    std::set<long> segmentit;
    for (std::uint32_t k = 0; k < 32; ++k) {
        if (const long a = osoite(k); a >= 0) segmentit.insert(a * 4 / 128);
    }
    return segmentit.size();
}

// Jaettu muisti: 32 pankkia, sana a on pankissa a % 32. Käsky kestää
// niin monta kierrosta kuin samaan pankkiin osuu eri sanoja.
std::size_t konflikti(const Osoite& osoite) {
    std::size_t pahin = 0;
    for (long pankki = 0; pankki < 32; ++pankki) {
        std::set<long> sanat;
        for (std::uint32_t k = 0; k < 32; ++k) {
            if (const long a = osoite(k); a >= 0 && a % 32 == pankki) {
                sanat.insert(a);
            }
        }
        pahin = std::max(pahin, sanat.size());
    }
    return pahin;
}
// @loppu malli

// Keskiarvo kaikkien aaltojen yli: aalto = työryhmän rivi ly (32 x 8).
struct Malli {
    double luku, kirjoitus;
    std::size_t jaettu;
};

Malli mallinna(int tapa) {
    double luku = 0, kirjoitus = 0;
    std::size_t aaltoja = 0, jaettu = 1;
    for (std::uint32_t gy = 0; gy < ryhmia(K, 32); ++gy) {
        for (std::uint32_t gx = 0; gx < ryhmia(L, 32); ++gx) {
            for (std::uint32_t ly = 0; ly < 8; ++ly) {
                const long x0 = gx * 32, y0 = gy * 32;
                const auto r = [&](long x, long y, long l, long k) {
                    return [=](std::uint32_t lx) -> long {
                        const long xx = x + lx;
                        return xx < l && y < k ? y * l + xx : -1;
                    };
                };
                if (tapa == 0) {  // suora: rivit gy*8 + ly
                    const long y = gy * 8 + ly;
                    if (y >= K) continue;
                    luku += static_cast<double>(segmentteja(r(x0, y, L, K)));
                    kirjoitus += static_cast<double>(segmentteja(
                        [&](std::uint32_t lx) -> long {
                            const long x = x0 + lx;
                            return x < L ? x * K + y : -1;
                        }));
                } else {          // laatta: 4 riviä säiettä kohden
                    for (long rr = 0; rr < 32; rr += 8) {
                        luku += static_cast<double>(
                            segmentteja(r(x0, y0 + ly + rr, L, K)));
                        kirjoitus += static_cast<double>(
                            segmentteja(r(y0, x0 + ly + rr, K, L)));
                    }
                    const long leveys = tapa == 2 ? 33 : 32;
                    jaettu = konflikti([&](std::uint32_t lx) {
                        return static_cast<long>(lx) * leveys + ly;
                    });
                }
                aaltoja += tapa == 0 ? 1 : 4;
            }
        }
    }
    return {luku / static_cast<double>(aaltoja),
            kirjoitus / static_cast<double>(aaltoja), jaettu};
}

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    VkYmparisto vk;
    Puskuri<std::uint32_t> lahde(vk, L * K), kohde(vk, L * K);
    for (std::uint32_t i = 0; i < L * K; ++i) lahde.alkiot()[i] = i;
    std::vector<std::uint32_t> odotettu(L * K);
    for (std::uint32_t y = 0; y < K; ++y) {
        for (std::uint32_t x = 0; x < L; ++x) {
            odotettu[x * K + y] = lahde.alkiot()[y * L + x];
        }
    }
    Ajastin ajastin(vk, 2);
    std::println("matriisi {} x {}, aalto 32 saietta, segmentti 128 t", L,
                 K);
    std::println("{:14} {:>10} {:>12} {:>10} {:>7}", "tapa",
                 "luku/aalto", "kirj./aalto", "pankit", "oikein");
    const char* nimet[] = {"suora", "laatta", "laatta+tayte"};
    for (int tapa = 0; tapa < 3; ++tapa) {
        // @alku putket
        Putki putki = tapa == 0
            ? Putki(vk, "bin/transpoosi_suora.spv", 2, sizeof(Vakiot))
            : Putki(vk, "bin/transpoosi_laatta.spv", 2, sizeof(Vakiot),
                    {{0, tapa == 2 ? 1u : 0u}});
        // @loppu putket
        const VkDescriptorSet j =
            putki.joukko({lahde.puskuri, kohde.puskuri});
        std::ranges::fill(kohde.alkiot(), 0u);
        VkCommandBuffer kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        const Ryhmat r = tapa == 0 ? Ryhmat{ryhmia(L, 32), ryhmia(K, 8)}
                                   : Ryhmat{ryhmia(L, 32), ryhmia(K, 32)};
        putki.aja(kp, j, Vakiot{L, K}, r);
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        const Malli m = mallinna(tapa);
        std::println("{:14} {:>10.2f} {:>12.2f} {:>10} {:>7}", nimet[tapa],
                     m.luku, m.kirjoitus,
                     tapa == 0 ? std::string("-")
                               : std::format("{}-kert.", m.jaettu),
                     kylla(eroavia<std::uint32_t>(kohde.alkiot(),
                                                  odotettu) == 0));
        if (mittaa) {
            std::println("    aika {:.2f} ms", ajastin.lue()[0] / 1e6);
        }
    }
    return Validointi::raportti();
}
