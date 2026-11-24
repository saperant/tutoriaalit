// Approksimointi: solmupeite maksimaalisen parituksen avulla
// (kerroin 2) ja joukkopeite ahneesti (kerroin ln n). Tuloksia
// verrataan raa'alla haulla laskettuun optimiin.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <print>
#include <vector>

#include "testaus.hpp"

struct Kaari {
    int u, v;
};

// @alku solmupeite
// Käydään kaaret läpi; jos kumpikaan pää ei ole vielä peitteessä,
// molemmat lisätään. Lisätyt kaaret muodostavat parituksen, ja jokaisen
// peitteen on sisällettävä vähintään yksi pää kustakin parituksen
// kaaresta: peite <= 2 |paritus| <= 2 OPT.
static std::uint32_t kaksi_approksimaatio(const std::vector<Kaari>& kaaret)
{
    std::uint32_t peite = 0;
    for (auto [u, v] : kaaret) {
        if (!((peite >> u) & 1) && !((peite >> v) & 1)) {
            peite |= (1u << u) | (1u << v);
        }
    }
    return peite;
}
// @loppu solmupeite

static int pienin_peite(int n, const std::vector<Kaari>& kaaret)
{
    int paras = n;
    for (std::uint32_t maski = 0; maski < (1u << n); ++maski) {
        bool kelpaa = std::ranges::all_of(kaaret, [&](Kaari k) {
            return ((maski >> k.u) & 1) || ((maski >> k.v) & 1);
        });
        if (kelpaa) {
            paras = std::min(paras, std::popcount(maski));
        }
    }
    return paras;
}

// @alku joukkopeite
// Ahne joukkopeite: valitaan aina joukko, joka peittää eniten vielä
// peittämättömiä alkioita. Tulos on enintään H(n) <= ln n + 1 kertaa
// optimi, eikä polynomiaikaisesti päästä olennaisesti parempaan,
// ellei P = NP.
static int ahne_peite(std::uint32_t kaikki,
                      const std::vector<std::uint32_t>& joukot)
{
    int valittu = 0;
    for (std::uint32_t peitetty = 0; peitetty != kaikki; ++valittu) {
        auto paras = std::ranges::max(joukot, {}, [&](std::uint32_t j) {
            return std::popcount(j & ~peitetty);
        });
        if ((paras & ~peitetty) == 0) {
            return -1;   // ei peitettävissä
        }
        peitetty |= paras;
    }
    return valittu;
}
// @loppu joukkopeite

static int pienin_joukkopeite(std::uint32_t kaikki,
                              const std::vector<std::uint32_t>& joukot)
{
    int paras = -1;
    auto m = joukot.size();
    for (std::uint32_t valinta = 0; valinta < (1u << m); ++valinta) {
        std::uint32_t peitetty = 0;
        for (std::size_t i = 0; i < m; ++i) {
            if ((valinta >> i) & 1) {
                peitetty |= joukot[i];
            }
        }
        int koko = std::popcount(valinta);
        if (peitetty == kaikki && (paras < 0 || koko < paras)) {
            paras = koko;
        }
    }
    return paras;
}

int main()
{
    // @alku testi
    double summa = 0, huonoin = 1;
    for (std::uint64_t siemen = 1; siemen <= 200; ++siemen) {
        Satunnainen s{siemen};
        int n = s.valilta(2, 14);
        std::vector<Kaari> kaaret;
        for (int u = 0; u < n; ++u) {
            for (int v = u + 1; v < n; ++v) {
                if (s.alle(4) == 0) {
                    kaaret.push_back({u, v});
                }
            }
        }
        if (kaaret.empty()) {
            continue;
        }
        s.sekoita(kaaret);
        auto peite = kaksi_approksimaatio(kaaret);
        int opt = pienin_peite(n, kaaret);
        double suhde = static_cast<double>(std::popcount(peite)) / opt;
        vaadi(std::ranges::all_of(kaaret, [&](Kaari k) {
                  return ((peite >> k.u) & 1) || ((peite >> k.v) & 1);
              }),
              "ei ole peite");
        vaadi(suhde <= 2, "kerroin ylittää 2");
        summa += suhde;
        huonoin = std::max(huonoin, suhde);
    }
    std::println("solmupeite:   suhde optimiin keskimäärin {:.2f}, "
                 "huonoin {:.2f} (raja 2)", summa / 200, huonoin);

    summa = 0;
    huonoin = 1;
    int kokeita = 0;
    for (std::uint64_t siemen = 1; kokeita < 200; ++siemen) {
        Satunnainen s{siemen};
        int alkioita = s.valilta(4, 16), m = s.valilta(3, 12);
        std::uint32_t kaikki = (1u << alkioita) - 1;
        std::vector<std::uint32_t> joukot(static_cast<std::size_t>(m));
        for (auto& j : joukot) {
            j = static_cast<std::uint32_t>(s.seuraava())
                & static_cast<std::uint32_t>(s.seuraava()) & kaikki;
        }
        int opt = pienin_joukkopeite(kaikki, joukot);
        if (opt < 0) {
            continue;   // joukot eivät peitä kaikkea: arvotaan uudet
        }
        ++kokeita;
        double suhde = static_cast<double>(ahne_peite(kaikki, joukot)) / opt;
        summa += suhde;
        huonoin = std::max(huonoin, suhde);
    }
    std::println("joukkopeite:  suhde optimiin keskimäärin {:.2f}, "
                 "huonoin {:.2f}", summa / kokeita, huonoin);
    // @loppu testi
}
