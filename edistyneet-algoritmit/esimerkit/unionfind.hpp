// unionfind.hpp: erillisten joukkojen yhdisteet (union-find).
//
// Malliparametrit valitsevat kaksi parannusta, jotta niiden vaikutus
// voidaan mitata erikseen: polun tiivistys ja yhdistäminen tason mukaan.
#pragma once

#include <numeric>
#include <utility>
#include <vector>

// @alku rakenne
template <bool Tiivistys, bool Tasot>
class UnionFind {
public:
    explicit UnionFind(int n)
        : vanhempi_(static_cast<std::size_t>(n)),
          taso_(static_cast<std::size_t>(n), 0), joukkoja_{n}
    {
        std::iota(vanhempi_.begin(), vanhempi_.end(), 0);
    }

    // Joukon edustaja eli puun juuri.
    int etsi(int x)
    {
        int juuri = x;
        while (vanhempi(juuri) != juuri) {
            juuri = vanhempi(juuri);
            ++askelia;
        }
        if constexpr (Tiivistys) {
            // Toinen kierros: jokainen polun solmu suoraan juuren alle.
            while (vanhempi(x) != juuri) {
                x = std::exchange(vanhempi(x), juuri);
            }
        }
        return juuri;
    }

    // Yhdistää joukot. Palauttaa false, jos a ja b olivat jo samassa.
    bool yhdista(int a, int b)
    {
        a = etsi(a);
        b = etsi(b);
        if (a == b) {
            return false;
        }
        if constexpr (Tasot) {
            // Matalampi puu liitetään korkeamman alle. Taso on yläraja
            // korkeudelle; se kasvaa vain, kun tasot ovat yhtä suuret.
            auto& ta = taso_[static_cast<std::size_t>(a)];
            auto& tb = taso_[static_cast<std::size_t>(b)];
            if (ta > tb) {
                std::swap(a, b);
            } else if (ta == tb) {
                ++tb;
            }
        }
        vanhempi(a) = b;
        --joukkoja_;
        return true;
    }

    bool samassa(int a, int b) { return etsi(a) == etsi(b); }
    int joukkoja() const { return joukkoja_; }

    long askelia = 0;   // etsi(): kuljettuja vanhempilinkkejä

private:
    int& vanhempi(int x) { return vanhempi_[static_cast<std::size_t>(x)]; }

    std::vector<int> vanhempi_;
    std::vector<int> taso_;
    int joukkoja_;
};
// @loppu rakenne

using Yhdisteet = UnionFind<true, true>;
