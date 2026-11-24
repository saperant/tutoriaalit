// Skip-lista: järjestetty linkitetty lista, jonka yläpuolella on
// harvenevia pikakaistoja. Solmun taso arvotaan, joten tasapaino on
// odotusarvoista eikä riipu syötteen järjestyksestä.
#include <array>
#include <cmath>
#include <memory>
#include <print>
#include <set>
#include <vector>

#include "testaus.hpp"

// @alku skiplista
class Skiplista {
public:
    static constexpr int maksimitaso = 24;

    explicit Skiplista(std::uint64_t siemen)
        : arpa_{siemen}, alku_{std::make_unique<Solmu>(0, maksimitaso)}
    {
    }

    // Lista vapautetaan silmukassa: unique_ptr-ketjun rekursiivinen
    // purku voisi pitkällä listalla ylittää pinon koon.
    ~Skiplista()
    {
        auto p = std::move(alku_->ensimmainen);
        while (p) {
            p = std::move(p->ensimmainen);
        }
    }
    Skiplista(const Skiplista&) = delete;
    Skiplista& operator=(const Skiplista&) = delete;

    bool sisaltaa(int x)
    {
        Solmu* p = edeltaja(x, nullptr);
        Solmu* q = p->seuraava[0];
        return q && q->avain == x;
    }

    // @alku lisays
    void lisaa(int x)
    {
        std::array<Solmu*, maksimitaso> polku{};
        Solmu* p = edeltaja(x, &polku);
        if (p->seuraava[0] && p->seuraava[0]->avain == x) {
            return;
        }
        int taso = arvo_taso();
        auto uusi = std::make_unique<Solmu>(x, taso);
        for (int i = 0; i < taso; ++i) {
            auto ii = static_cast<std::size_t>(i);
            uusi->seuraava[ii] = polku[ii]->seuraava[ii];
            polku[ii]->seuraava[ii] = uusi.get();
        }
        // Omistus kulkee tasolla 0.
        uusi->ensimmainen = std::move(p->ensimmainen);
        p->ensimmainen = std::move(uusi);
    }
    // @loppu lisays

    void poista(int x)
    {
        std::array<Solmu*, maksimitaso> polku{};
        Solmu* p = edeltaja(x, &polku);
        Solmu* q = p->seuraava[0];
        if (!q || q->avain != x) {
            return;
        }
        for (std::size_t i = 0; i < q->seuraava.size(); ++i) {
            polku[i]->seuraava[i] = q->seuraava[i];
        }
        p->ensimmainen = std::move(q->ensimmainen);   // q vapautuu
    }

    // Korkein käytössä oleva taso.
    int korkein() const
    {
        int k = 0;
        while (k < maksimitaso
               && alku_->seuraava[static_cast<std::size_t>(k)]) {
            ++k;
        }
        return k;
    }

    long askelia = 0;   // haun siirtymät eteenpäin linkkejä pitkin

private:
    struct Solmu {
        Solmu(int a, int taso)
            : avain{a}, seuraava(static_cast<std::size_t>(taso), nullptr)
        {
        }
        int avain;
        std::vector<Solmu*> seuraava;           // taso 0 on koko lista
        std::unique_ptr<Solmu> ensimmainen;     // omistaa seuraava[0]:n
    };

    // Taso k todennäköisyydellä 2^-k: kolikkoa heitetään, kunnes tulee
    // kruuna. Odotusarvoisesti 2 osoitinta solmua kohden.
    int arvo_taso()
    {
        int taso = 1;
        while (taso < maksimitaso && arpa_.alle(2) == 0) {
            ++taso;
        }
        return taso;
    }

    // @alku haku
    // Laskeutuu ylimmältä tasolta: kullakin tasolla edetään, kunnes
    // seuraava avain olisi >= x. Palauttaa x:n edeltäjän tasolla 0.
    Solmu* edeltaja(int x, std::array<Solmu*, maksimitaso>* polku)
    {
        Solmu* p = alku_.get();
        for (int i = maksimitaso - 1; i >= 0; --i) {
            auto ii = static_cast<std::size_t>(i);
            while (p->seuraava[ii] && p->seuraava[ii]->avain < x) {
                p = p->seuraava[ii];
                ++askelia;
            }
            if (polku) {
                (*polku)[ii] = p;
            }
        }
        return p;
    }
    // @loppu haku

    Satunnainen arpa_;
    std::unique_ptr<Solmu> alku_;   // vartijasolmu, ei avainta
};
// @loppu skiplista

int main()
{
    // @alku testi
    for (std::uint64_t siemen = 1; siemen <= 30; ++siemen) {
        Satunnainen s{siemen};
        Skiplista lista{siemen + 99};
        std::set<int> malli;
        for (int i = 0; i < 2000; ++i) {
            int x = s.valilta(0, 299);
            switch (s.alle(3)) {
            case 0:
                lista.poista(x);
                malli.erase(x);
                break;
            case 1:
                lista.lisaa(x);
                malli.insert(x);
                break;
            default:
                vaadi(lista.sisaltaa(x) == malli.contains(x),
                      "haku poikkeaa");
            }
        }
    }
    std::println("vertailutesti: 30 ajoa x 2000 operaatiota, 0 eroa");
    // @loppu testi

    // @alku mittaus
    for (int n : {1000, 100000}) {
        Skiplista lista{7};
        for (int x = 0; x < n; ++x) {
            lista.lisaa(x);   // järjestys ei vaikuta tasapainoon
        }
        lista.askelia = 0;
        Satunnainen s{1};
        for (int i = 0; i < 10000; ++i) {
            lista.sisaltaa(s.valilta(0, n - 1));
        }
        std::println("n = {:6}: {:4.1f} askelta/haku, log2 n = {:4.1f}, "
                     "korkein taso {}", n,
                     static_cast<double>(lista.askelia) / 10000,
                     std::log2(n), lista.korkein());
    }
    // @loppu mittaus
}
