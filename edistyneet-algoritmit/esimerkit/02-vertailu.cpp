// Satunnaistettu vertailutesti: järjestetyllä taulukolla toteutettua
// joukkoa verrataan std::set-malliin satunnaisella operaatiosarjalla.
#include <algorithm>
#include <print>
#include <set>
#include <vector>

#include "testaus.hpp"

// @alku toteutus
// Järjestetty taulukko joukkona ("flat set"): haku O(log n), lisäys ja
// poisto O(n), mutta alkiot ovat peräkkäin muistissa.
class JarjestettyJoukko {
public:
    bool lisaa(int x)
    {
        auto p = std::ranges::lower_bound(alkiot_, x);
        if (p != alkiot_.end() && *p == x) {
            return false;
        }
        alkiot_.insert(p, x);
        return true;
    }

    bool poista(int x)
    {
        auto p = std::ranges::lower_bound(alkiot_, x);
        if (p == alkiot_.end() || *p != x) {
            return false;
        }
        alkiot_.erase(p);
        return true;
    }

    bool sisaltaa(int x) const
    {
        return std::ranges::binary_search(alkiot_, x);
    }

    // Pienin alkio, joka on >= x, tai -1.
    int alaraja(int x) const
    {
        auto p = std::ranges::lower_bound(alkiot_, x);
        return p == alkiot_.end() ? -1 : *p;
    }

    const std::vector<int>& alkiot() const { return alkiot_; }

    // Invariantti: aidosti kasvava järjestys.
    bool kunnossa() const
    {
        return std::ranges::adjacent_find(alkiot_, std::greater_equal{})
               == alkiot_.end();
    }

private:
    std::vector<int> alkiot_;
};
// @loppu toteutus

// @alku testi
// Yksi testiajo: n satunnaista operaatiota avaimilla 0..avaimia-1.
// Pieni avainavaruus takaa, että samat avaimet toistuvat ja poistot
// osuvat olemassa oleviin alkioihin.
static int vertaa(std::uint64_t siemen, int n, int avaimia)
{
    Satunnainen s{siemen};
    JarjestettyJoukko joukko;
    std::set<int> malli;
    for (int i = 0; i < n; ++i) {
        int x = s.valilta(0, avaimia - 1);
        bool ok = true;
        switch (s.alle(4)) {
        case 0:
            ok = joukko.lisaa(x) == malli.insert(x).second;
            break;
        case 1:
            ok = joukko.poista(x) == (malli.erase(x) == 1);
            break;
        case 2:
            ok = joukko.sisaltaa(x) == malli.contains(x);
            break;
        default: {
            auto p = malli.lower_bound(x);
            ok = joukko.alaraja(x) == (p == malli.end() ? -1 : *p);
        }
        }
        vaadi(ok, "tulos poikkeaa mallista");
        vaadi(joukko.kunnossa(), "invariantti rikki");
    }
    vaadi(std::ranges::equal(joukko.alkiot(), malli),
          "sisältö poikkeaa mallista");
    return static_cast<int>(malli.size());
}
// @loppu testi

int main()
{
    // @alku ajot
    for (int avaimia : {4, 64, 4096}) {
        int koot = 0;
        for (std::uint64_t siemen = 1; siemen <= 20; ++siemen) {
            koot += vertaa(siemen, 2000, avaimia);
        }
        std::println("avaimia {:4}: 20 ajoa x 2000 operaatiota, "
                     "joukon keskikoko lopuksi {}", avaimia, koot / 20);
    }
    // @loppu ajot
}
