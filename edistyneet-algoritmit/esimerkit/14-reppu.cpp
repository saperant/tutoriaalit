// 0/1-reppuongelma kolmella tavalla: peruuttava haku, haarautuminen ja
// karsinta murto-osarajalla sekä dynaaminen ohjelmointi kapasiteetin
// yli (pseudopolynominen O(n W)).
#include <algorithm>
#include <numeric>
#include <print>
#include <vector>

#include "testaus.hpp"

struct Esine {
    int paino, arvo;
};

// @alku peruutus
// Peruuttava haku: jokainen esine joko mukaan tai pois. Ylipainoinen
// haara katkaistaan, muuten käydään läpi kaikki 2^n osajoukkoa.
struct Peruutus {
    const std::vector<Esine>& e;
    int paras = 0;
    long solmuja = 0;

    void hae(std::size_t i, int tilaa, int arvo)
    {
        ++solmuja;
        paras = std::max(paras, arvo);
        if (i == e.size()) {
            return;
        }
        if (e[i].paino <= tilaa) {
            hae(i + 1, tilaa - e[i].paino, arvo + e[i].arvo);
        }
        hae(i + 1, tilaa, arvo);
    }
};
// @loppu peruutus

// @alku karsinta
// Haarautuminen ja karsinta: esineet arvotiheyden mukaan laskevasti.
// Yläraja haaralle on murto-osainen reppu: täytetään ahneesti ja
// viimeisestä esineestä otetaan osa. Jos raja ei ylitä parasta
// löydettyä ratkaisua, haaraa ei tutkita.
struct Karsinta {
    const std::vector<Esine>& e;   // järjestetty arvo/paino laskevasti
    int paras = 0;
    long solmuja = 0;

    double raja(std::size_t i, int tilaa, int arvo) const
    {
        double r = arvo;
        for (; i < e.size() && e[i].paino <= tilaa; ++i) {
            tilaa -= e[i].paino;
            r += e[i].arvo;
        }
        if (i < e.size()) {
            r += static_cast<double>(e[i].arvo) * tilaa / e[i].paino;
        }
        return r;
    }

    void hae(std::size_t i, int tilaa, int arvo)
    {
        ++solmuja;
        paras = std::max(paras, arvo);
        if (i == e.size() || raja(i, tilaa, arvo) <= paras) {
            return;
        }
        if (e[i].paino <= tilaa) {   // ahne haara ensin: hyvä ratkaisu
            hae(i + 1, tilaa - e[i].paino, arvo + e[i].arvo);   // nopeasti
        }
        hae(i + 1, tilaa, arvo);
    }
};
// @loppu karsinta

// @alku dp
// paras[w] = suurin arvo painolla enintään w; kapasiteetti käydään
// takaperin, jotta kukin esine tulee mukaan korkeintaan kerran.
static int dynaaminen(const std::vector<Esine>& e, int kapasiteetti)
{
    std::vector<int> paras(static_cast<std::size_t>(kapasiteetti) + 1, 0);
    for (auto [p, a] : e) {
        for (int w = kapasiteetti; w >= p; --w) {
            auto wi = static_cast<std::size_t>(w);
            paras[wi] = std::max(paras[wi],
                                 paras[wi - static_cast<std::size_t>(p)] + a);
        }
    }
    return paras.back();
}
// @loppu dp

int main()
{
    // @alku vertailu
    // Arvo korreloi painon kanssa, kuten oikeissa tehtävissä (isompi
    // esine on arvokkaampi): karsinta on silloin vaikeampaa.
    long peruutus_solmuja = 0, karsinta_solmuja = 0;
    constexpr int kokeita = 20;
    for (std::uint64_t siemen = 1; siemen <= kokeita; ++siemen) {
        Satunnainen s{siemen};
        std::vector<Esine> e(20);
        for (auto& x : e) {
            x.paino = s.valilta(10, 100);
            x.arvo = x.paino + s.valilta(0, 20);
        }
        int kapasiteetti =
            std::accumulate(e.begin(), e.end(), 0,
                            [](int a, Esine x) { return a + x.paino; }) / 2;
        Peruutus p{e};
        p.hae(0, kapasiteetti, 0);
        auto jarjestetty = e;
        std::ranges::sort(jarjestetty, [](Esine a, Esine b) {
            return a.arvo * b.paino > b.arvo * a.paino;   // ilman jakoa
        });
        Karsinta k{jarjestetty};
        k.hae(0, kapasiteetti, 0);
        int odotettu = dynaaminen(e, kapasiteetti);
        vaadi(p.paras == odotettu && k.paras == odotettu,
              "ratkaisut poikkeavat");
        peruutus_solmuja += p.solmuja;
        karsinta_solmuja += k.solmuja;
    }
    std::println("{} tehtävää, 20 esinettä: kaikki kolme samaa mieltä",
                 kokeita);
    std::println("{:<26} {:8} hakusolmua/tehtävä", "peruuttava haku",
                 peruutus_solmuja / kokeita);
    std::println("{:<26} {:8} hakusolmua/tehtävä",
                 "karsinta murto-osarajalla", karsinta_solmuja / kokeita);
    // @loppu vertailu
}
