// Mallinnus minimileikkauksena: projektien valinta. Projekti tuottaa
// rahaa mutta vaatii investointeja, joista osa on yhteisiä. Paras
// valinta luetaan minimileikkauksesta, ja tulos tarkistetaan käymällä
// läpi kaikki projektijoukot.
#include <algorithm>
#include <array>
#include <print>
#include <string_view>
#include <vector>

#include "testaus.hpp"
#include "virtaus.hpp"

struct Vaatimus {
    int projekti, investointi;
};

// @alku malli
// Lähde -> projekti (tuotto), investointi -> nielu (hinta) ja
// projekti -> investointi (ääretön). Äärellinen leikkaus ei voi katkaista
// ääretöntä kaarta, joten lähteen puolelle jäävän projektin kaikki
// investoinnit ovat samalla puolella. Leikkauksen kapasiteetti on
// hylättyjen projektien tuotot + tehtyjen investointien hinnat, joten
// paras voitto = tuottojen summa - minimileikkaus.
static long paras_voitto(const std::vector<long>& tuotto,
                         const std::vector<long>& hinta,
                         const std::vector<Vaatimus>& vaatimukset,
                         std::vector<bool>& valittu)
{
    const long aareton = 1'000'000'000;
    int p = static_cast<int>(tuotto.size());
    int q = static_cast<int>(hinta.size());
    int s = p + q, t = p + q + 1;
    Virtausverkko verkko{p + q + 2};
    long summa = 0;
    for (int i = 0; i < p; ++i) {
        verkko.lisaa_kaari(s, i, tuotto[static_cast<std::size_t>(i)]);
        summa += tuotto[static_cast<std::size_t>(i)];
    }
    for (int j = 0; j < q; ++j) {
        verkko.lisaa_kaari(p + j, t, hinta[static_cast<std::size_t>(j)]);
    }
    for (auto [i, j] : vaatimukset) {
        verkko.lisaa_kaari(i, p + j, aareton);
    }
    long leikkaus = verkko.dinic(s, t);
    auto puoli = verkko.s_puoli(s);
    valittu.assign(puoli.begin(), puoli.begin() + p);
    return summa - leikkaus;
}
// @loppu malli

// Raaka vertailu: jokainen projektijoukko ja sen vaatimat investoinnit.
static long raaka(const std::vector<long>& tuotto,
                  const std::vector<long>& hinta,
                  const std::vector<Vaatimus>& vaatimukset)
{
    long paras = 0;
    for (unsigned joukko = 0; joukko < (1u << tuotto.size()); ++joukko) {
        std::vector<bool> tarvitaan(hinta.size(), false);
        long voitto = 0;
        for (std::size_t i = 0; i < tuotto.size(); ++i) {
            if ((joukko >> i) & 1) {
                voitto += tuotto[i];
            }
        }
        for (auto [i, j] : vaatimukset) {
            if ((joukko >> i) & 1) {
                tarvitaan[static_cast<std::size_t>(j)] = true;
            }
        }
        for (std::size_t j = 0; j < hinta.size(); ++j) {
            voitto -= tarvitaan[j] ? hinta[j] : 0;
        }
        paras = std::max(paras, voitto);
    }
    return paras;
}

int main()
{
    for (std::uint64_t siemen = 1; siemen <= 300; ++siemen) {
        Satunnainen s{siemen};
        std::vector<long> tuotto(static_cast<std::size_t>(s.valilta(1, 7)));
        std::vector<long> hinta(static_cast<std::size_t>(s.valilta(1, 6)));
        for (auto& x : tuotto) {
            x = s.valilta(1, 20);
        }
        for (auto& x : hinta) {
            x = s.valilta(1, 20);
        }
        std::vector<Vaatimus> vaatimukset;
        for (int i = 0; i < static_cast<int>(tuotto.size()); ++i) {
            for (int j = 0; j < static_cast<int>(hinta.size()); ++j) {
                if (s.alle(3) == 0) {
                    vaatimukset.push_back({i, j});
                }
            }
        }
        std::vector<bool> valittu;
        vaadi(paras_voitto(tuotto, hinta, vaatimukset, valittu)
                  == raaka(tuotto, hinta, vaatimukset),
              "minimileikkaus ei anna parasta voittoa");
    }
    std::println("vertailutesti: 300 tapausta, leikkaus = paras valinta");

    // @alku esimerkki
    // Tuotot ja hinnat tuhansina euroina.
    constexpr std::array<std::string_view, 4> projekti{
        "verkkokauppa", "raportointi", "mobiilisovellus", "arkistointi"};
    constexpr std::array<std::string_view, 3> investointi{
        "maksurajapinta", "tietovarasto", "tunnistautuminen"};
    const std::vector<long> tuotto{40, 15, 25, 5};
    const std::vector<long> hinta{30, 20, 12};
    const std::vector<Vaatimus> vaatimukset{
        {0, 0}, {0, 2}, {1, 1}, {2, 0}, {2, 2}, {3, 1}};
    std::vector<bool> valittu;
    long voitto = paras_voitto(tuotto, hinta, vaatimukset, valittu);
    std::print("paras voitto {} t€, projektit:", voitto);
    for (std::size_t i = 0; i < projekti.size(); ++i) {
        if (valittu[i]) {
            std::print(" {}", projekti[i]);
        }
    }
    std::print("\ninvestoinnit:");
    for (std::size_t j = 0; j < investointi.size(); ++j) {
        bool tarvitaan = false;
        for (auto [i, k] : vaatimukset) {
            tarvitaan = tarvitaan || (valittu[static_cast<std::size_t>(i)]
                                      && static_cast<std::size_t>(k) == j);
        }
        if (tarvitaan) {
            std::print(" {}", investointi[j]);
        }
    }
    std::println("");
    // @loppu esimerkki
}
