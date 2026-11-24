// Segmenttipuu: välikyselyt mille tahansa liitännäiselle operaatiolle
// ja laiska päivitys välien lisäyksille.
#include <algorithm>
#include <functional>
#include <limits>
#include <print>
#include <string>
#include <vector>

#include "testaus.hpp"

// @alku segmentti
// Iteratiivinen segmenttipuu: lehdet ovat indekseissä n ... 2n - 1 ja
// solmun i lapset 2i ja 2i + 1. Operaation on oltava liitännäinen
// (a * b) * c = a * (b * c), mutta ei vaihdannainen: vasen ja oikea
// tulos kootaan erikseen, jotta järjestys säilyy.
template <class T, class Op>
class Segmenttipuu {
public:
    // arvot ei saa olla tyhjä.
    Segmenttipuu(const std::vector<T>& arvot, T neutraali, Op op = {})
        : n_{arvot.size()}, puu_(2 * n_, neutraali), neutraali_{neutraali},
          op_{op}
    {
        std::ranges::copy(arvot, puu_.begin()
                                     + static_cast<std::ptrdiff_t>(n_));
        for (std::size_t i = n_ - 1; i >= 1; --i) {
            puu_[i] = op_(puu_[2 * i], puu_[2 * i + 1]);
        }
    }

    void aseta(std::size_t i, T arvo)
    {
        i += n_;
        puu_[i] = std::move(arvo);
        for (i /= 2; i >= 1; i /= 2) {
            puu_[i] = op_(puu_[2 * i], puu_[2 * i + 1]);
        }
    }

    // Välin [a, b) tulos.
    T kysy(std::size_t a, std::size_t b) const
    {
        T vasen = neutraali_, oikea = neutraali_;
        for (a += n_, b += n_; a < b; a /= 2, b /= 2) {
            if (a % 2 == 1) {
                vasen = op_(vasen, puu_[a++]);
            }
            if (b % 2 == 1) {
                oikea = op_(puu_[--b], oikea);
            }
        }
        return op_(vasen, oikea);
    }

private:
    std::size_t n_;
    std::vector<T> puu_;
    T neutraali_;
    Op op_;
};
// @loppu segmentti

// @alku laiska
// Laiska segmenttipuu: välin lisäys ja välin maksimi. Solmun lykatty
// lisäys koskee koko sen alipuuta, ja se työnnetään lapsille vasta, kun
// rekursio laskeutuu niihin. Molemmat operaatiot ovat O(log n).
class Varaukset {
public:
    explicit Varaukset(int n)
        : n_{n}, maksimi_(4 * static_cast<std::size_t>(n), 0),
          lykatty_(4 * static_cast<std::size_t>(n), 0)
    {
    }

    void lisaa(int a, int b, int d) { lisaa(1, 0, n_, a, b, d); }
    int maksimi(int a, int b) { return maksimi(1, 0, n_, a, b); }

private:
    void tyonna(std::size_t i)
    {
        for (std::size_t c : {2 * i, 2 * i + 1}) {
            maksimi_[c] += lykatty_[i];
            lykatty_[c] += lykatty_[i];
        }
        lykatty_[i] = 0;
    }

    // Solmu i kattaa välin [l, r).
    void lisaa(std::size_t i, int l, int r, int a, int b, int d)
    {
        if (b <= l || r <= a) {
            return;
        }
        if (a <= l && r <= b) {   // koko solmu: lisäys lykätään
            maksimi_[i] += d;
            lykatty_[i] += d;
            return;
        }
        tyonna(i);
        int m = l + (r - l) / 2;
        lisaa(2 * i, l, m, a, b, d);
        lisaa(2 * i + 1, m, r, a, b, d);
        maksimi_[i] = std::max(maksimi_[2 * i], maksimi_[2 * i + 1]);
    }

    int maksimi(std::size_t i, int l, int r, int a, int b)
    {
        if (b <= l || r <= a) {
            return std::numeric_limits<int>::min();
        }
        if (a <= l && r <= b) {
            return maksimi_[i];
        }
        tyonna(i);
        int m = l + (r - l) / 2;
        return std::max(maksimi(2 * i, l, m, a, b),
                        maksimi(2 * i + 1, m, r, a, b));
    }

    int n_;
    std::vector<int> maksimi_, lykatty_;
};
// @loppu laiska

struct Pienin {
    int operator()(int a, int b) const { return std::min(a, b); }
};

int main()
{
    // @alku testi
    // Minimi ja merkkijonojen katenaatio: jälkimmäinen ei ole
    // vaihdannainen, joten se paljastaa järjestysvirheet.
    for (std::uint64_t siemen = 1; siemen <= 20; ++siemen) {
        Satunnainen s{siemen};
        auto n = static_cast<std::size_t>(s.valilta(1, 64));
        std::vector<int> luvut(n);
        std::vector<std::string> sanat(n);
        for (std::size_t i = 0; i < n; ++i) {
            luvut[i] = s.valilta(-99, 99);
            sanat[i] = std::string(1, static_cast<char>('a' + i % 26));
        }
        Segmenttipuu pienin{luvut, std::numeric_limits<int>::max(),
                            Pienin{}};
        Segmenttipuu jono{sanat, std::string{}, std::plus<std::string>{}};
        for (int op = 0; op < 500; ++op) {
            auto a = s.alle(n), b = s.alle(n + 1);
            if (s.alle(3) == 0) {
                luvut[a] = s.valilta(-99, 99);
                pienin.aseta(a, luvut[a]);
                sanat[a] = std::string(1, static_cast<char>('A' + op % 26));
                jono.aseta(a, sanat[a]);
            } else if (a < b) {
                auto alku = luvut.begin() + static_cast<std::ptrdiff_t>(a);
                auto loppu = luvut.begin() + static_cast<std::ptrdiff_t>(b);
                vaadi(pienin.kysy(a, b) == *std::min_element(alku, loppu),
                      "minimi poikkeaa");
                std::string odotettu;
                for (auto i = a; i < b; ++i) {
                    odotettu += sanat[i];
                }
                vaadi(jono.kysy(a, b) == odotettu, "katenaatio poikkeaa");
            }
        }
    }
    // Laiska puu: vertailu taulukkoon, jossa lisäys käy välin läpi.
    for (std::uint64_t siemen = 1; siemen <= 20; ++siemen) {
        Satunnainen s{siemen};
        int n = s.valilta(1, 100);
        Varaukset puu{n};
        std::vector<int> malli(static_cast<std::size_t>(n), 0);
        for (int op = 0; op < 1000; ++op) {
            int a = s.valilta(0, n - 1), b = s.valilta(a + 1, n);
            auto alku = malli.begin() + a, loppu = malli.begin() + b;
            if (s.alle(2) == 0) {
                int d = s.valilta(-5, 5);
                puu.lisaa(a, b, d);
                std::for_each(alku, loppu, [d](int& x) { x += d; });
            } else {
                vaadi(puu.maksimi(a, b) == *std::max_element(alku, loppu),
                      "maksimi poikkeaa");
            }
        }
    }
    std::println("vertailutesti: minimi, katenaatio ja laiska maksimi");
    // @loppu testi

    // @alku varaukset
    // Kokoustila 20 hengelle vuodeksi: varaus [a, b) hyväksytään, jos
    // jokaisena päivänä on tilaa kaikille.
    Satunnainen s{5};
    Varaukset kaytto{365};
    int hyvaksytty = 0, hylatty = 0;
    for (int i = 0; i < 2000; ++i) {
        int alku = s.valilta(0, 359), kesto = s.valilta(1, 5);
        int henkia = s.valilta(1, 8);
        int loppu = std::min(alku + kesto, 365);
        if (kaytto.maksimi(alku, loppu) + henkia <= 20) {
            kaytto.lisaa(alku, loppu, henkia);
            ++hyvaksytty;
        } else {
            ++hylatty;
        }
    }
    std::println("varauksia {} hyväksytty, {} hylätty; suurin käyttö {}",
                 hyvaksytty, hylatty, kaytto.maksimi(0, 365));
    // @loppu varaukset
}
