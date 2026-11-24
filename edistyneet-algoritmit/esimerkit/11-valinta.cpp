// Satunnaistetut algoritmit: Las Vegas -tyyppinen pikavalinta (aina
// oikein, aika satunnainen) ja Monte Carlo -tyyppinen Freivaldsin
// tarkistus (aina nopea, voi erehtyä).
#include <algorithm>
#include <print>
#include <vector>

#include "testaus.hpp"

static long vertailuja = 0;

// @alku valinta
// k:nneksi pienin (k = 0, ...). Jako kolmeen osaan: < jakoalkio,
// = jakoalkio, > jakoalkio; rekursio jatkuu vain yhteen osaan.
// Satunnainen jakoalkio: odotusarvoisesti alle 4n vertailua millä
// tahansa syötteellä.
template <class Valitsin>
static int valitse(std::vector<int> a, std::size_t k, Valitsin jakoalkio)
{
    for (;;) {
        int j = a[jakoalkio(a.size())];
        std::vector<int> pienet, suuret;
        std::size_t yhtasuuria = 0;
        for (int x : a) {
            ++vertailuja;
            if (x < j) {
                pienet.push_back(x);
            } else if (x > j) {
                suuret.push_back(x);
            } else {
                ++yhtasuuria;
            }
        }
        if (k < pienet.size()) {
            a = std::move(pienet);
        } else if (k < pienet.size() + yhtasuuria) {
            return j;
        } else {
            k -= pienet.size() + yhtasuuria;
            a = std::move(suuret);
        }
    }
}
// @loppu valinta

// @alku freivalds
using Matriisi = std::vector<std::vector<long>>;

static std::vector<long> kerro(const Matriisi& m, const std::vector<long>& x)
{
    std::vector<long> y(m.size(), 0);
    for (std::size_t i = 0; i < m.size(); ++i) {
        for (std::size_t j = 0; j < x.size(); ++j) {
            y[i] += m[i][j] * x[j];
        }
    }
    return y;
}

// Tarkistaa, onko A B = C, ajassa O(k n^2) laskematta tuloa (O(n^3)).
// Satunnaisella 0/1-vektorilla x: jos A B != C, niin A (B x) != C x
// todennäköisyydellä vähintään 1/2. Väärä "kyllä" k kierroksen jälkeen:
// enintään 2^-k. Oikeaa tuloa algoritmi ei koskaan hylkää.
static bool freivalds(const Matriisi& a, const Matriisi& b,
                      const Matriisi& c, int kierroksia, Satunnainen& s)
{
    for (int i = 0; i < kierroksia; ++i) {
        std::vector<long> x(a.size());
        for (auto& xi : x) {
            xi = static_cast<long>(s.alle(2));
        }
        if (kerro(a, kerro(b, x)) != kerro(c, x)) {
            return false;   // varmasti väärin
        }
    }
    return true;   // todennäköisesti oikein
}
// @loppu freivalds

int main()
{
    Satunnainen s{12};
    // @alku testi
    for (int koe = 0; koe < 300; ++koe) {
        std::vector<int> a(static_cast<std::size_t>(s.valilta(1, 50)));
        for (int& x : a) {
            x = s.valilta(0, 20);   // paljon yhtä suuria
        }
        auto k = s.alle(a.size());
        auto jarjestetty = a;
        std::ranges::sort(jarjestetty);
        vaadi(valitse(a, k, [&](std::size_t n) { return s.alle(n); })
                  == jarjestetty[k],
              "valinta poikkeaa");
    }
    std::println("vertailutesti: 300 valintaa, 0 eroa");
    // @loppu testi

    // @alku vertailut
    constexpr int n = 5000;
    std::vector<int> nouseva(n);
    for (int i = 0; i < n; ++i) {
        nouseva[static_cast<std::size_t>(i)] = i;
    }
    vertailuja = 0;
    valitse(nouseva, n / 2, [](std::size_t) { return std::size_t{0}; });
    std::println("mediaani, ensimmäinen jakoalkiona:  {:10} vertailua",
                 vertailuja);
    vertailuja = 0;
    for (int i = 0; i < 10; ++i) {
        valitse(nouseva, n / 2, [&](std::size_t m) { return s.alle(m); });
    }
    std::println("mediaani, satunnainen jakoalkio:    {:10} vertailua "
                 "(keskiarvo, n = {})", vertailuja / 10, n);
    // @loppu vertailut

    // @alku tarkistus
    constexpr std::size_t m = 60;
    Matriisi a(m, std::vector<long>(m)), b = a, c = a;
    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t j = 0; j < m; ++j) {
            a[i][j] = s.valilta(-9, 9);
            b[i][j] = s.valilta(-9, 9);
        }
    }
    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t k = 0; k < m; ++k) {
            for (std::size_t j = 0; j < m; ++j) {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    int hyvaksytty = 0;
    for (int i = 0; i < 1000; ++i) {
        hyvaksytty += freivalds(a, b, c, 1, s) ? 1 : 0;
    }
    std::println("oikea tulo:           hyväksytty {} / 1000", hyvaksytty);
    c[37][18] += 1;   // yksi virheellinen alkio
    for (int kierroksia : {1, 10}) {
        hyvaksytty = 0;
        for (int i = 0; i < 1000; ++i) {
            hyvaksytty += freivalds(a, b, c, kierroksia, s) ? 1 : 0;
        }
        std::println("virhe, {:2} kierrosta: hyväksytty {} / 1000",
                     kierroksia, hyvaksytty);
    }
    // @loppu tarkistus
}
