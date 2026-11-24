// Pikaoppaan tiiviit toteutukset ja niiden vertailutesti.
#include <numeric>
#include <print>
#include <string_view>
#include <vector>

#include "testaus.hpp"

// @alku fenwick
struct Fenwick {   // indeksit 0 ... n-1
    std::vector<long> t;
    explicit Fenwick(int n) : t(static_cast<std::size_t>(n) + 1) {}
    void lisaa(int i, long d)
    {
        for (auto j = static_cast<std::size_t>(i) + 1; j < t.size();
             j += j & -j) {
            t[j] += d;
        }
    }
    long summa(int i) const   // [0, i)
    {
        long s = 0;
        for (auto j = static_cast<std::size_t>(i); j > 0; j -= j & -j) {
            s += t[j];
        }
        return s;
    }
};
// @loppu fenwick

// @alku uf
struct UF {   // polun puolitus + koko
    std::vector<int> p, koko;
    explicit UF(int n)
        : p(static_cast<std::size_t>(n)), koko(static_cast<std::size_t>(n), 1)
    {
        std::iota(p.begin(), p.end(), 0);
    }
    int& v(int x) { return p[static_cast<std::size_t>(x)]; }
    int& k(int x) { return koko[static_cast<std::size_t>(x)]; }
    int etsi(int x)
    {
        while (v(x) != x) {
            x = v(x) = v(v(x));
        }
        return x;
    }
    bool yhdista(int a, int b)
    {
        a = etsi(a);
        b = etsi(b);
        if (a == b) {
            return false;
        }
        if (k(a) > k(b)) {
            std::swap(a, b);   // pienempi suuremman alle
        }
        v(a) = b;
        k(b) += k(a);
        return true;
    }
};
// @loppu uf

// @alku vika
std::vector<int> vika(std::string_view p)
{
    std::vector<int> f(p.size(), 0);
    for (std::size_t j = 1, k = 0; j < p.size(); ++j) {
        while (k > 0 && p[j] != p[k]) {
            k = static_cast<std::size_t>(f[k - 1]);
        }
        k += p[j] == p[k] ? 1 : 0;
        f[j] = static_cast<int>(k);
    }
    return f;
}
// @loppu vika

int main()
{
    // @alku vertailu
    Satunnainen s{1};
    Fenwick f{50};
    std::vector<long> malli(50, 0);
    UF uf{50};
    std::vector<int> nimio(50);
    std::iota(nimio.begin(), nimio.end(), 0);
    for (int op = 0; op < 5000; ++op) {
        int a = s.valilta(0, 49), b = s.valilta(0, 49);
        f.lisaa(a, b);
        malli[static_cast<std::size_t>(a)] += b;
        vaadi(f.summa(b) == std::accumulate(malli.begin(),
                                            malli.begin() + b, 0L),
              "summa");
        int la = nimio[static_cast<std::size_t>(a)];
        int lb = nimio[static_cast<std::size_t>(b)];
        vaadi(uf.yhdista(a, b) == (la != lb), "yhdista");
        for (int& l : nimio) {
            l = l == la ? lb : l;
        }
    }
    std::println("Fenwick ja union-find: 5000 operaatiota, 0 eroa");
    // @loppu vertailu
    std::print("vika(abacabab) =");
    for (int x : vika("abacabab")) {
        std::print(" {}", x);
    }
    std::println("");
}
