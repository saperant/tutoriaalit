// Fenwick-puu (binäärinen indeksipuu): etuliitesummat ja pistepäivitykset
// ajassa O(log n) yhdellä taulukolla.
#include <print>
#include <vector>

#include "testaus.hpp"

// @alku fenwick
// Solmu i (1-pohjainen) tallentaa välin (i - alin(i), i] summan, missä
// alin(i) = i & -i on i:n alin ykkösbitti.
class Fenwick {
public:
    explicit Fenwick(int n) : puu_(static_cast<std::size_t>(n) + 1, 0) {}

    // Lisää d indeksin i (0-pohjainen) arvoon.
    void lisaa(int i, long d)
    {
        for (++i; i < koko(); i += i & -i) {
            puu_[static_cast<std::size_t>(i)] += d;
        }
    }

    // Etuliitesumma: indeksien 0 ... i - 1 arvojen summa.
    long summa(int i) const
    {
        long s = 0;
        for (; i > 0; i -= i & -i) {
            s += puu_[static_cast<std::size_t>(i)];
        }
        return s;
    }

    long valisumma(int a, int b) const { return summa(b) - summa(a); }

    // Pienin i, jolla summa(i + 1) > k, kun arvot ovat ei-negatiivisia.
    // Laskeutuu puussa bitti kerrallaan suurimmasta alkaen: O(log n).
    int etsi(long k) const
    {
        int i = 0;
        int bitti = 1;
        while (2 * bitti < koko()) {
            bitti *= 2;
        }
        for (; bitti > 0; bitti /= 2) {
            int j = i + bitti;
            if (j < koko() && puu_[static_cast<std::size_t>(j)] <= k) {
                i = j;
                k -= puu_[static_cast<std::size_t>(j)];
            }
        }
        return i;   // 0-pohjainen indeksi
    }

private:
    int koko() const { return static_cast<int>(puu_.size()); }

    std::vector<long> puu_;
};
// @loppu fenwick

int main()
{
    // Rakenteen muoto 16 alkiolle samoilla bittikaavoilla kuin luokassa:
    // kirjan kuva piirretään näistä riveistä (kaaviot/tee.py).
    std::print("solmujen välit:");
    for (int i = 1; i <= 16; ++i) {
        std::print(" {}:({},{}]", i, i - (i & -i), i);
    }
    std::print("\nsumma(13) lukee solmut:");
    for (int i = 13; i > 0; i -= i & -i) {
        std::print(" {}", i);
    }
    std::print("\nlisaa(4, d) päivittää solmut:");
    for (int i = 4 + 1; i <= 16; i += i & -i) {
        std::print(" {}", i);
    }
    std::println("\n");

    // @alku testi
    for (std::uint64_t siemen = 1; siemen <= 20; ++siemen) {
        Satunnainen s{siemen};
        int n = s.valilta(1, 300);
        Fenwick f{n};
        std::vector<long> malli(static_cast<std::size_t>(n), 0);
        for (int op = 0; op < 3000; ++op) {
            int a = s.valilta(0, n - 1), b = s.valilta(0, n);
            if (s.alle(2) == 0) {
                long d = s.valilta(0, 9);   // ei-negatiivinen: etsi() toimii
                f.lisaa(a, d);
                malli[static_cast<std::size_t>(a)] += d;
            } else if (a <= b) {
                long odotettu = 0;
                for (int i = a; i < b; ++i) {
                    odotettu += malli[static_cast<std::size_t>(i)];
                }
                vaadi(f.valisumma(a, b) == odotettu, "välisumma poikkeaa");
            }
            long kaikki = f.summa(n);
            if (kaikki > 0) {
                long k = s.valilta(0, static_cast<int>(kaikki) - 1);
                int i = 0;
                long kertyma = malli[0];
                while (kertyma <= k) {   // raakahaku: kertymä ylittää k:n
                    kertyma += malli[static_cast<std::size_t>(++i)];
                }
                vaadi(f.etsi(k) == i, "etsi poikkeaa");
            }
        }
    }
    std::println("vertailutesti: 20 taulukkoa x 3000 operaatiota");
    // @loppu testi

    // @alku mediaani
    // Liukuva mediaani vasteajoista: taulukko laskee kunkin millisekunti-
    // arvon esiintymät, ja etsi() löytää k:nnen arvon.
    Satunnainen s{11};
    Fenwick lukumaarat{1000};
    std::vector<int> ikkuna;
    for (int i = 1; i <= 10000; ++i) {
        int ms = s.valilta(20, 80) + (s.alle(50) == 0 ? 600 : 0);
        ikkuna.push_back(ms);
        lukumaarat.lisaa(ms, 1);
        if (ikkuna.size() > 1001) {   // 1001 viimeisintä
            lukumaarat.lisaa(ikkuna[ikkuna.size() - 1002], -1);
        }
        if (i % 2500 == 0) {
            long n = std::min<long>(i, 1001);
            std::println("pyyntö {:5}: mediaani {} ms, 99. persentiili "
                         "{} ms", i, lukumaarat.etsi(n / 2),
                         lukumaarat.etsi(n * 99 / 100));
        }
    }
    // @loppu mediaani
}
