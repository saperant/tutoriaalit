// Haku kolmesta säiliöstä: std::map, järjestetty vektori ja
// std::unordered_map. Solmupohjaiset säiliöt hajottavat datan kekoon.
#include <algorithm>
#include <cstddef>
#include <map>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

#include "laskuri.hpp"
#include "mittari.hpp"
#include "satunnainen.hpp"

// @alku jarjestetty
// Järjestetty vektori "litteänä karttana": haku puolittamalla.
// C++23:n std::flat_map (GCC 15:stä alkaen) on sama ajatus valmiina.
class LiteaKartta {
public:
    explicit LiteaKartta(std::vector<std::pair<int, int>> parit)
        : parit_{std::move(parit)}
    {
        std::ranges::sort(parit_);
    }

    const int* hae(int avain) const
    {
        auto it = std::ranges::lower_bound(
            parit_, avain, {}, &std::pair<int, int>::first);
        return it != parit_.end() && it->first == avain ? &it->second
                                                         : nullptr;
    }

private:
    std::vector<std::pair<int, int>> parit_;
};
// @loppu jarjestetty

struct Aineisto {
    std::map<int, int> puu;
    std::unordered_map<int, int> hajautus;
    LiteaKartta litea{{}};
    std::vector<int> haettavat;
    std::size_t varaukset_puu = 0;
    std::size_t varaukset_hajautus = 0;
    std::size_t varaukset_litea = 0;
};

Aineisto luo(int n, int hakuja)
{
    Aineisto a;
    Satunnainen s{11};
    std::vector<std::pair<int, int>> parit;
    for (int i = 0; i < n; ++i) {
        parit.emplace_back(static_cast<int>(s.alle(1u << 30)), i);
    }
    {
        laskuri::Jakso j;
        a.puu = std::map<int, int>(parit.begin(), parit.end());
        a.varaukset_puu = j.varaukset();
    }
    {
        laskuri::Jakso j;
        a.hajautus = std::unordered_map<int, int>(parit.begin(),
                                                  parit.end());
        a.varaukset_hajautus = j.varaukset();
    }
    {
        laskuri::Jakso j;
        a.litea = LiteaKartta{parit};
        a.varaukset_litea = j.varaukset();
    }
    for (int i = 0; i < hakuja; ++i) {
        a.haettavat.push_back(parit[s.alle(static_cast<unsigned>(n))].first);
    }
    return a;
}

// @alku haut
template <typename Hae>
long hae_kaikki(const std::vector<int>& avaimet, Hae hae)
{
    long summa = 0;
    for (int k : avaimet) {
        summa += hae(k);
    }
    return summa;
}

[[gnu::noinline]] long hae_puu(const Aineisto& a)
{
    return hae_kaikki(a.haettavat,
                      [&](int k) { return a.puu.find(k)->second; });
}

[[gnu::noinline]] long hae_hajautus(const Aineisto& a)
{
    return hae_kaikki(a.haettavat,
                      [&](int k) { return a.hajautus.find(k)->second; });
}

[[gnu::noinline]] long hae_litea(const Aineisto& a)
{
    return hae_kaikki(a.haettavat, [&](int k) { return *a.litea.hae(k); });
}
// @loppu haut

template <typename Toimi>
void valitse(std::string_view tapa, const Aineisto& a, Toimi toimi)
{
    if (tapa == "map") {
        toimi([&] { mittari::pida(hae_puu(a)); });
    } else if (tapa == "unordered_map") {
        toimi([&] { mittari::pida(hae_hajautus(a)); });
    } else if (tapa == "litea") {
        toimi([&] { mittari::pida(hae_litea(a)); });
    }
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    auto a = tila.mittaa ? luo(1'000'000, 100'000) : luo(20'000, 1000);
    if (tila.mittaa) {
        std::printf("100000 hakua, 1000000 avainta\n");
        double vertailu = 0;
        for (std::string_view t : {"map", "litea", "unordered_map"}) {
            valitse(t, a, [&](auto f) {
                auto m = mittari::mittaa(f, 21);
                mittari::tulosta(t, m, vertailu);
                vertailu = vertailu == 0 ? m.mediaani_ms : vertailu;
            });
        }
        return 0;
    }
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, a, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    std::printf("hakujen summa: map %ld, litea %ld, unordered_map %ld\n",
                hae_puu(a), hae_litea(a), hae_hajautus(a));
    std::printf("varauksia rakentaessa: map %zu, litea %zu, "
                "unordered_map %zu\n",
                a.varaukset_puu, a.varaukset_litea, a.varaukset_hajautus);
}
