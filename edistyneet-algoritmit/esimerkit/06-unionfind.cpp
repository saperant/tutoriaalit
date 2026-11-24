// Union-findin parannusten vaikutus ja vertailutesti nimiötaulukkoa
// vastaan.
#include <print>
#include <vector>

#include "testaus.hpp"
#include "unionfind.hpp"

// @alku malli
// Malli: jokaisella alkiolla on joukon nimiö, ja yhdistäminen nimeää
// toisen joukon kaikki alkiot uudelleen. O(n) yhdistämistä kohden, mutta
// niin yksinkertainen, että sen oikeellisuus näkyy suoraan.
struct Nimiot {
    std::vector<int> nimio;
    int joukkoja;

    explicit Nimiot(int n) : nimio(static_cast<std::size_t>(n)), joukkoja{n}
    {
        for (int i = 0; i < n; ++i) {
            nimio[static_cast<std::size_t>(i)] = i;
        }
    }

    bool yhdista(int a, int b)
    {
        int la = nimio[static_cast<std::size_t>(a)];
        int lb = nimio[static_cast<std::size_t>(b)];
        if (la == lb) {
            return false;
        }
        for (int& l : nimio) {
            if (l == la) {
                l = lb;
            }
        }
        --joukkoja;
        return true;
    }
};
// @loppu malli

template <bool T, bool R>
void vertaa(std::uint64_t siemen)
{
    Satunnainen s{siemen};
    constexpr int n = 100;
    UnionFind<T, R> uf{n};
    Nimiot malli{n};
    for (int i = 0; i < 3000; ++i) {
        int a = s.valilta(0, n - 1), b = s.valilta(0, n - 1);
        if (s.alle(3) == 0) {
            vaadi(uf.yhdista(a, b) == malli.yhdista(a, b), "yhdistä");
        } else {
            bool sama = malli.nimio[static_cast<std::size_t>(a)]
                        == malli.nimio[static_cast<std::size_t>(b)];
            vaadi(uf.samassa(a, b) == sama, "samassa");
        }
        vaadi(uf.joukkoja() == malli.joukkoja, "joukkojen määrä");
    }
}

// @alku mittaus
// Kolme tapaa rakentaa yksi n alkion joukko; sen jälkeen mitataan
// n satunnaisen haun keskimääräinen polun pituus.
// Ketju yhdistää alkiot järjestyksessä, parit yhdistävät yhtä suuria
// joukkoja (1+1, 2+2, 4+4, ...), ja satunnainen yhdistää satunnaisia
// pareja.
template <bool T, bool R>
void mittaa(const char* nimi)
{
    constexpr int n = 8192;
    UnionFind<T, R> ketju{n}, parit{n}, satunnainen{n};
    Satunnainen s{3};
    // @alku kuormat
    for (int i = 0; i + 1 < n; ++i) {
        ketju.yhdista(i, i + 1);
    }
    for (int askel = 1; askel < n; askel *= 2) {
        for (int i = 0; i + askel < n; i += 2 * askel) {
            parit.yhdista(i, i + askel);
        }
    }
    while (satunnainen.joukkoja() > 1) {
        // Argumenttien laskentajärjestys ei ole määrätty: arvonnat
        // omille riveilleen, jotta GCC ja Clang saavat saman sarjan.
        int a = s.valilta(0, n - 1);
        int b = s.valilta(0, n - 1);
        satunnainen.yhdista(a, b);
    }
    // @loppu kuormat
    auto haut = [&](auto& uf) {
        uf.askelia = 0;
        for (int i = 0; i < n; ++i) {
            uf.etsi(s.valilta(0, n - 1));
        }
        return static_cast<double>(uf.askelia) / n;
    };
    double k = haut(ketju), p = haut(parit), r = haut(satunnainen);
    std::println("{:<17} {:8.2f} {:8.2f} {:12.2f}", nimi, k, p, r);
}
// @loppu mittaus

int main()
{
    for (std::uint64_t siemen = 1; siemen <= 10; ++siemen) {
        vertaa<false, false>(siemen);
        vertaa<true, false>(siemen);
        vertaa<false, true>(siemen);
        vertaa<true, true>(siemen);
    }
    std::println("vertailutesti: 4 muunnelmaa x 10 ajoa x 3000 operaatiota");
    std::println("{:<17} {:>8} {:>8} {:>12}", "askelia/haku", "ketju",
                 "parit", "satunnainen");
    mittaa<false, false>("ei parannuksia");
    mittaa<true, false>("polun tiivistys");
    mittaa<false, true>("tasot");
    mittaa<true, true>("molemmat");
}
