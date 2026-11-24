// Treap: hakupuu avaimille ja keko satunnaisille prioriteeteille.
// Operaatiot rakentuvat kahdesta perusoperaatiosta, jaosta ja
// yhdistämisestä. Koon ylläpito antaa järjestystilastot.
#include <algorithm>
#include <cmath>
#include <iterator>
#include <memory>
#include <print>
#include <set>
#include <utility>

#include "testaus.hpp"

class Treap {
public:
    explicit Treap(std::uint64_t siemen) : arpa_{siemen} {}

    bool sisaltaa(int x) const
    {
        const Solmu* h = juuri_.get();
        while (h && h->avain != x) {
            h = x < h->avain ? h->vasen.get() : h->oikea.get();
        }
        return h != nullptr;
    }

    // @alku operaatiot
    // @alku lisays
    void lisaa(int x)
    {
        if (sisaltaa(x)) {
            return;
        }
        auto [pienet, suuret] = jaa(std::move(juuri_), x);
        auto uusi = std::make_unique<Solmu>(x, arpa_.seuraava());
        juuri_ = yhdista(yhdista(std::move(pienet), std::move(uusi)),
                         std::move(suuret));
    }

    // Kaksi jakoa erottavat avaimen x omaksi puukseen. (x + 1 ei saa
    // ylivuotaa; tämän esimerkin avaimet ovat pieniä.)
    void poista(int x)
    {
        auto [pienet, loput] = jaa(std::move(juuri_), x);
        auto [x_solmu, suuret] = jaa(std::move(loput), x + 1);
        // x_solmu (korkeintaan yksi solmu) vapautuu tässä.
        juuri_ = yhdista(std::move(pienet), std::move(suuret));
    }
    // @loppu lisays

    // k:nneksi pienin avain, k = 0, 1, ..., koko() - 1.
    int kas(int k) const
    {
        const Solmu* h = juuri_.get();
        for (;;) {
            int vasemmalla = koko(h->vasen);
            if (k < vasemmalla) {
                h = h->vasen.get();
            } else if (k == vasemmalla) {
                return h->avain;
            } else {
                k -= vasemmalla + 1;
                h = h->oikea.get();
            }
        }
    }

    // Avaimia, jotka ovat pienempiä kuin x.
    int jarjestysluku(int x) const
    {
        int tulos = 0;
        for (const Solmu* h = juuri_.get(); h;) {
            if (x <= h->avain) {
                h = h->vasen.get();
            } else {
                tulos += koko(h->vasen) + 1;
                h = h->oikea.get();
            }
        }
        return tulos;
    }
    // @loppu operaatiot

    int koko() const { return koko(juuri_); }
    int korkeus() const { return korkeus(juuri_.get()); }

private:
    struct Solmu {
        Solmu(int a, std::uint64_t p) : avain{a}, prioriteetti{p} {}
        int avain;
        std::uint64_t prioriteetti;   // keko-ominaisuus: vanhempi suurin
        int koko = 1;                 // alipuun solmujen määrä
        std::unique_ptr<Solmu> vasen, oikea;
    };
    using Osoitin = std::unique_ptr<Solmu>;

    static int koko(const Osoitin& h) { return h ? h->koko : 0; }

    static void paivita(Solmu& h)
    {
        h.koko = 1 + koko(h.vasen) + koko(h.oikea);
    }

    // @alku jako
    // Jakaa puun kahtia: avaimet < x ja avaimet >= x. Polku kulkee
    // juuresta lehteen, joten aika on O(korkeus).
    static std::pair<Osoitin, Osoitin> jaa(Osoitin h, int x)
    {
        if (!h) {
            return {nullptr, nullptr};
        }
        if (h->avain < x) {
            auto [a, b] = jaa(std::move(h->oikea), x);
            h->oikea = std::move(a);
            paivita(*h);
            return {std::move(h), std::move(b)};
        }
        auto [a, b] = jaa(std::move(h->vasen), x);
        h->vasen = std::move(b);
        paivita(*h);
        return {std::move(a), std::move(h)};
    }

    // Yhdistää puut, kun kaikki a:n avaimet ovat pienempiä kuin b:n.
    // Juureksi nousee suuremman prioriteetin solmu.
    static Osoitin yhdista(Osoitin a, Osoitin b)
    {
        if (!a || !b) {
            return a ? std::move(a) : std::move(b);
        }
        if (a->prioriteetti > b->prioriteetti) {
            a->oikea = yhdista(std::move(a->oikea), std::move(b));
            paivita(*a);
            return a;
        }
        b->vasen = yhdista(std::move(a), std::move(b->vasen));
        paivita(*b);
        return b;
    }
    // @loppu jako

    static int korkeus(const Solmu* h)
    {
        return h ? 1 + std::max(korkeus(h->vasen.get()),
                                korkeus(h->oikea.get()))
                 : 0;
    }

    Satunnainen arpa_;
    Osoitin juuri_;
};

int main()
{
    // @alku testi
    int operaatioita = 0;
    for (std::uint64_t siemen = 1; siemen <= 30; ++siemen) {
        Satunnainen s{siemen};
        Treap puu{siemen + 1000};
        std::set<int> malli;
        for (int i = 0; i < 1500; ++i, ++operaatioita) {
            int x = s.valilta(0, 199);
            switch (s.alle(4)) {
            case 0:
                puu.poista(x);
                malli.erase(x);
                break;
            case 1: {
                auto pienempia = std::distance(malli.begin(),
                                               malli.lower_bound(x));
                vaadi(puu.jarjestysluku(x) == pienempia,
                      "järjestysluku poikkeaa");
                break;
            }
            default:
                puu.lisaa(x);
                malli.insert(x);
            }
            vaadi(puu.koko() == static_cast<int>(malli.size()),
                  "koko poikkeaa");
            if (!malli.empty()) {
                int k = s.valilta(0, puu.koko() - 1);
                vaadi(puu.kas(k) == *std::next(malli.begin(), k),
                      "k:s alkio poikkeaa");
            }
        }
    }
    std::println("vertailutesti: {} operaatiota, 0 eroa", operaatioita);
    // @loppu testi

    // @alku korkeus
    for (int n : {1000, 100000}) {
        Treap puu{42};
        for (int x = 0; x < n; ++x) {
            puu.lisaa(x);
        }
        std::println("n = {:6}: korkeus {:2}, odotettu syvyys "
                     "2 ln n = {:4.1f}", n, puu.korkeus(),
                     2 * std::log(n));
    }
    // @loppu korkeus
}
