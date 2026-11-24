// Virheellisen toteutuksen löytäminen vertailutestillä ja virheen
// aiheuttavan operaatiosarjan pienentäminen.
#include <algorithm>
#include <optional>
#include <print>
#include <set>
#include <vector>

#include "testaus.hpp"

// @alku virhe
// Kuten luvun alun JarjestettyJoukko, mutta poista() unohtaa tarkistaa,
// että löydetty alkio on etsitty. Jos x puuttuu, se poistaa seuraavan
// suuremman alkion.
class VirheellinenJoukko {
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

    // @alku poista
    bool poista(int x)
    {
        auto p = std::ranges::lower_bound(alkiot_, x);
        if (p == alkiot_.end()) {   // puuttuu: *p != x
            return false;
        }
        alkiot_.erase(p);
        return true;
    }
    // @loppu poista

    bool sisaltaa(int x) const
    {
        return std::ranges::binary_search(alkiot_, x);
    }

private:
    std::vector<int> alkiot_;
};
// @loppu virhe

// @alku sarja
enum class Tyyppi { lisaa, poista, sisaltaa };

struct Operaatio {
    Tyyppi tyyppi;
    int avain;
};

using Sarja = std::vector<Operaatio>;

// Ajaa sarjan toteutukselle ja mallille. Palauttaa ensimmäisen
// poikkeavan operaation indeksin tai tyhjän, jos tulokset täsmäävät.
static std::optional<std::size_t> aja(const Sarja& sarja)
{
    VirheellinenJoukko joukko;
    std::set<int> malli;
    for (std::size_t i = 0; i < sarja.size(); ++i) {
        auto [tyyppi, x] = sarja[i];
        bool ok = true;
        if (tyyppi == Tyyppi::lisaa) {
            ok = joukko.lisaa(x) == malli.insert(x).second;
        } else if (tyyppi == Tyyppi::poista) {
            ok = joukko.poista(x) == (malli.erase(x) == 1);
        } else {
            ok = joukko.sisaltaa(x) == malli.contains(x);
        }
        if (!ok) {
            return i;
        }
    }
    return std::nullopt;
}
// @loppu sarja

static Sarja satunnainen_sarja(std::uint64_t siemen, int n)
{
    Satunnainen s{siemen};
    Sarja sarja;
    for (int i = 0; i < n; ++i) {
        auto tyyppi = static_cast<Tyyppi>(s.alle(3));
        sarja.push_back({tyyppi, s.valilta(0, 999)});
    }
    return sarja;
}

// @alku pienennys
// Ahne pienennys: poistetaan ensin puolikkaita, sitten neljänneksiä ja
// lopulta yksittäisiä operaatioita aina, kun sarja epäonnistuu yhä.
// Lopuksi avaimia pienennetään, kunnes yksikään ei enää pienene.
static Sarja pienenna(Sarja sarja)
{
    for (std::size_t pala = sarja.size() / 2; pala >= 1; pala /= 2) {
        std::size_t i = 0;
        while (i < sarja.size()) {
            Sarja koe = sarja;
            auto alku = koe.begin() + static_cast<std::ptrdiff_t>(i);
            auto loppu = koe.begin()
                + static_cast<std::ptrdiff_t>(std::min(i + pala, koe.size()));
            koe.erase(alku, loppu);
            if (aja(koe)) {
                sarja = std::move(koe);   // virhe säilyi: pala pois
            } else {
                i += pala;
            }
        }
    }
    for (bool muuttui = true; muuttui;) {
        muuttui = false;
        for (auto& op : sarja) {
            int alkuperainen = op.avain;
            for (int pienempi = 0; pienempi < alkuperainen; ++pienempi) {
                op.avain = pienempi;
                if (aja(sarja)) {
                    muuttui = true;
                    break;
                }
                op.avain = alkuperainen;
            }
        }
    }
    return sarja;
}
// @loppu pienennys

static const char* nimi(Tyyppi t)
{
    switch (t) {
    case Tyyppi::lisaa:
        return "lisaa";
    case Tyyppi::poista:
        return "poista";
    default:
        return "sisaltaa";
    }
}

int main()
{
    // @alku haku
    for (std::uint64_t siemen = 1; siemen <= 1000; ++siemen) {
        Sarja sarja = satunnainen_sarja(siemen, 300);
        auto kohta = aja(sarja);
        if (!kohta) {
            continue;
        }
        std::println("virhe: siemen {}, operaatio {}/{}", siemen,
                     *kohta + 1, sarja.size());
        sarja.resize(*kohta + 1);
        Sarja pieni = pienenna(sarja);
        std::println("pienennetty {} -> {} operaatiota:", sarja.size(),
                     pieni.size());
        for (auto [tyyppi, x] : pieni) {
            std::println("  {} {}", nimi(tyyppi), x);
        }
        break;
    }
    // @loppu haku
}
