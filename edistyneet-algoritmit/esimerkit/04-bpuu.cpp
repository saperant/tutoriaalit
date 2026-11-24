// B-puu: monihaarainen hakupuu, jonka solmu täyttää kokonaisen levy-
// lohkon tai useita välimuistirivejä. Lisäys halkaisee täydet solmut
// matkalla alas (Cormen ym.), joten paluumatkaa ei tarvita.
#include <algorithm>
#include <memory>
#include <optional>
#include <print>
#include <set>
#include <string>
#include <vector>

#include "testaus.hpp"

// @alku rakenne
// Minimiaste t: jokaisessa solmussa juurta lukuun ottamatta on
// t - 1 ... 2t - 1 avainta, ja sisäsolmulla on yksi lapsi enemmän kuin
// avaimia. Kaikki lehdet ovat samalla syvyydellä.
class BPuu {
public:
    explicit BPuu(int t) : t_{t}, juuri_{std::make_unique<Solmu>()} {}

    struct Laskurit {
        long solmuja = 0;     // luettuja solmuja (levylohkoja)
        long vertailuja = 0;  // avainvertailuja solmujen sisällä
    };

    bool sisaltaa(int x, Laskurit& l) const
    {
        for (const Solmu* h = juuri_.get(); h;) {
            ++l.solmuja;
            std::size_t i = paikka(*h, x, l);
            if (i < h->avaimet.size() && h->avaimet[i] == x) {
                return true;
            }
            h = h->lehti() ? nullptr : h->lapset[i].get();
        }
        return false;
    }
    // @loppu rakenne

    // Pienin avain, joka on >= x.
    std::optional<int> alaraja(int x) const
    {
        Laskurit l;
        std::optional<int> paras;
        for (const Solmu* h = juuri_.get(); h;) {
            std::size_t i = paikka(*h, x, l);
            if (i < h->avaimet.size()) {
                paras = h->avaimet[i];
                if (h->avaimet[i] == x) {
                    break;
                }
            }
            h = h->lehti() ? nullptr : h->lapset[i].get();
        }
        return paras;
    }

    // @alku lisays
    void lisaa(int x)
    {
        Laskurit l;
        if (sisaltaa(x, l)) {
            return;
        }
        if (taysi(*juuri_)) {
            // Puu kasvaa vain juuresta: uusi juuri, jonka ainoa lapsi
            // halkaistaan. Siksi kaikki lehdet pysyvät samalla syvyydellä.
            auto uusi = std::make_unique<Solmu>();
            uusi->lapset.push_back(std::move(juuri_));
            juuri_ = std::move(uusi);
            halkaise(*juuri_, 0);
        }
        Solmu* h = juuri_.get();
        while (!h->lehti()) {
            std::size_t i = paikka(*h, x, l);
            if (taysi(*h->lapset[i])) {
                halkaise(*h, i);
                if (x > h->avaimet[i]) {
                    ++i;
                }
            }
            h = h->lapset[i].get();
        }
        h->avaimet.insert(h->avaimet.begin()
                              + static_cast<std::ptrdiff_t>(paikka(*h, x, l)),
                          x);
    }
    // @loppu lisays

    int korkeus() const
    {
        int k = 1;
        for (const Solmu* h = juuri_.get(); !h->lehti();
             h = h->lapset[0].get()) {
            ++k;
        }
        return k;
    }

    // Täyttöaste: avaimia suhteessa solmujen kapasiteettiin.
    double tayttoaste() const
    {
        long avaimia = 0, solmuja = 0;
        laske(*juuri_, avaimia, solmuja);
        return static_cast<double>(avaimia)
               / static_cast<double>(solmuja * (2 * t_ - 1));
    }

    std::vector<int> alkiot() const
    {
        std::vector<int> tulos;
        sisajarjestys(*juuri_, tulos);
        return tulos;
    }

    // @alku invariantit
    std::optional<std::string> tarkista() const
    {
        std::optional<std::string> rike;
        int lehtisyvyys = -1;
        tarkista(*juuri_, true, 0, lehtisyvyys, rike);
        return rike;
    }
    // @loppu invariantit

private:
    struct Solmu {
        std::vector<int> avaimet;
        std::vector<std::unique_ptr<Solmu>> lapset;   // tyhjä lehdessä
        bool lehti() const { return lapset.empty(); }
    };

    bool taysi(const Solmu& h) const
    {
        return static_cast<int>(h.avaimet.size()) == 2 * t_ - 1;
    }

    // Binäärihaku solmun sisällä: ensimmäinen avain, joka on >= x.
    static std::size_t paikka(const Solmu& h, int x, Laskurit& l)
    {
        std::size_t ala = 0, yla = h.avaimet.size();
        while (ala < yla) {
            std::size_t keski = ala + (yla - ala) / 2;
            ++l.vertailuja;
            if (h.avaimet[keski] < x) {
                ala = keski + 1;
            } else {
                yla = keski;
            }
        }
        return ala;
    }

    // @alku halkaisu
    // Halkaisee vanhemman p täyden lapsen i: keskimmäinen avain nousee
    // vanhempaan, ja sen oikealla puolella olevat siirtyvät uuteen
    // sisarukseen. Molempiin jää t - 1 avainta.
    void halkaise(Solmu& p, std::size_t i)
    {
        Solmu& y = *p.lapset[i];
        auto z = std::make_unique<Solmu>();
        auto t = static_cast<std::ptrdiff_t>(t_);
        int keski = y.avaimet[t_ - 1];
        z->avaimet.assign(y.avaimet.begin() + t, y.avaimet.end());
        y.avaimet.resize(static_cast<std::size_t>(t_ - 1));
        if (!y.lehti()) {
            z->lapset.assign(std::make_move_iterator(y.lapset.begin() + t),
                             std::make_move_iterator(y.lapset.end()));
            y.lapset.resize(static_cast<std::size_t>(t_));
        }
        auto ii = static_cast<std::ptrdiff_t>(i);
        p.avaimet.insert(p.avaimet.begin() + ii, keski);
        p.lapset.insert(p.lapset.begin() + ii + 1, std::move(z));
    }
    // @loppu halkaisu

    static void laske(const Solmu& h, long& avaimia, long& solmuja)
    {
        avaimia += static_cast<long>(h.avaimet.size());
        ++solmuja;
        for (const auto& c : h.lapset) {
            laske(*c, avaimia, solmuja);
        }
    }

    static void sisajarjestys(const Solmu& h, std::vector<int>& tulos)
    {
        for (std::size_t i = 0; i < h.avaimet.size(); ++i) {
            if (!h.lehti()) {
                sisajarjestys(*h.lapset[i], tulos);
            }
            tulos.push_back(h.avaimet[i]);
        }
        if (!h.lehti()) {
            sisajarjestys(*h.lapset.back(), tulos);
        }
    }

    void tarkista(const Solmu& h, bool juuri, int syvyys, int& lehtisyvyys,
                  std::optional<std::string>& rike) const
    {
        auto n = static_cast<int>(h.avaimet.size());
        if (n > 2 * t_ - 1 || (!juuri && n < t_ - 1)) {
            rike = "avainten määrä rajojen ulkopuolella";
        } else if (!std::ranges::is_sorted(h.avaimet)) {
            rike = "solmun avaimet eivät ole järjestyksessä";
        } else if (!h.lehti() && h.lapset.size() != h.avaimet.size() + 1) {
            rike = "lapsia ei ole yhtä enemmän kuin avaimia";
        } else if (h.lehti() && lehtisyvyys >= 0 && syvyys != lehtisyvyys) {
            rike = "lehdet eri syvyyksillä";
        }
        if (h.lehti()) {
            lehtisyvyys = syvyys;
        }
        for (const auto& c : h.lapset) {
            tarkista(*c, false, syvyys + 1, lehtisyvyys, rike);
        }
    }

    int t_;
    std::unique_ptr<Solmu> juuri_;
};

int main()
{
    // @alku testi
    // Vertailutesti std::set-mallia vastaan pienellä asteella, jolloin
    // halkaisuja tulee paljon. Sisäjärjestyksen on oltava aidosti
    // kasvava, mikä kattaa myös avainten rajat alipuiden välillä.
    for (int t : {2, 3, 5}) {
        for (std::uint64_t siemen = 1; siemen <= 10; ++siemen) {
            Satunnainen s{siemen};
            BPuu puu{t};
            std::set<int> malli;
            for (int i = 0; i < 2000; ++i) {
                int x = s.valilta(0, 2999);
                BPuu::Laskurit l;
                if (s.alle(2) == 0) {
                    puu.lisaa(x);
                    malli.insert(x);
                } else {
                    vaadi(puu.sisaltaa(x, l) == malli.contains(x),
                          "haku poikkeaa");
                }
                auto p = malli.lower_bound(x);
                auto odotettu = p == malli.end() ? std::optional<int>{}
                                                 : std::optional{*p};
                vaadi(puu.alaraja(x) == odotettu, "alaraja poikkeaa");
            }
            if (auto rike = puu.tarkista()) {
                vaadi(false, *rike);
            }
            vaadi(puu.alkiot() == std::vector(malli.begin(), malli.end()),
                  "sisältö poikkeaa mallista");
        }
    }
    std::println("vertailutesti: asteet 2, 3 ja 5, 60 000 operaatiota");
    // @loppu testi

    // @alku lohkot
    constexpr int n = 100000;
    std::vector<int> avaimet(n);
    for (int i = 0; i < n; ++i) {
        avaimet[static_cast<std::size_t>(i)] = 2 * i;
    }
    Satunnainen s{7};
    s.sekoita(avaimet);
    std::println("{:>5} {:>8} {:>13} {:>14} {:>11}", "t", "korkeus",
                 "solmuja/haku", "vertailuja", "täyttöaste");
    for (int t : {2, 4, 16, 64, 256}) {
        BPuu puu{t};
        for (int x : avaimet) {
            puu.lisaa(x);
        }
        BPuu::Laskurit l;
        for (int x = 0; x < 2 * n; x += 2) {
            vaadi(puu.sisaltaa(x, l), "avain puuttuu");
        }
        std::println("{:5} {:8} {:13.2f} {:14.2f} {:10.0f} %", t,
                     puu.korkeus(), static_cast<double>(l.solmuja) / n,
                     static_cast<double>(l.vertailuja) / n,
                     100 * puu.tayttoaste());
    }
    // @loppu lohkot
}
