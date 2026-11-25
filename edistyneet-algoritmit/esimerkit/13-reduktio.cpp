// Polynomiaalinen reduktio 3-SAT -> riippumaton joukko. Reduktio
// testataan satunnaisilla kaavoilla: kaava toteutuu täsmälleen silloin,
// kun verkossa on m solmun riippumaton joukko.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <print>
#include <vector>

#include "testaus.hpp"

// @alku kaava
// Literaali +v tai -v (muuttujat 1 ... n), lauseke on kolmen literaalin
// disjunktio ja kaava lausekkeiden konjunktio.
using Lauseke = std::array<int, 3>;
using Kaava = std::vector<Lauseke>;

// Varmentaja: annettu sijoitus tarkistetaan ajassa O(m). Tämä tekee
// 3-SAT:sta NP-ongelman: kyllä-vastauksen todistus on lyhyt ja nopea
// tarkistaa, vaikka sen löytäminen voi olla vaikeaa.
static bool toteuttaa(const Kaava& f, const std::vector<bool>& arvo)
{
    for (const auto& lauseke : f) {
        bool tosi = false;
        for (int l : lauseke) {
            auto v = static_cast<std::size_t>(std::abs(l));
            tosi = tosi || arvo[v] == (l > 0);
        }
        if (!tosi) {
            return false;
        }
    }
    return true;
}

// Raaka haku: kaikki 2^n sijoitusta.
static bool toteutuva(const Kaava& f, int n)
{
    std::vector<bool> arvo(static_cast<std::size_t>(n) + 1);
    for (unsigned maski = 0; maski < (1u << n); ++maski) {
        for (int v = 1; v <= n; ++v) {
            arvo[static_cast<std::size_t>(v)] = (maski >> (v - 1)) & 1;
        }
        if (toteuttaa(f, arvo)) {
            return true;
        }
    }
    return false;
}
// @loppu kaava

// @alku reduktio
// Jokaisesta lausekkeesta kolmio (kolme solmua, yksi kutakin literaalia
// kohden), ja ristiriitaiset literaalit x ja -x yhdistetään kaarella.
// Riippumaton joukko voi ottaa kustakin kolmiosta enintään yhden
// solmun eikä koskaan sekä x:ää että -x:ää. m solmun joukko valitsee
// siis kustakin lausekkeesta yhden ristiriidattoman todeksi tehtävän
// literaalin. Verkossa on 3m solmua ja O(m^2) kaarta: polynominen.
using Verkko = std::vector<std::vector<bool>>;   // vierusmatriisi

static Verkko reduktio(const Kaava& f)
{
    std::size_t n = 3 * f.size();
    Verkko g(n, std::vector<bool>(n, false));
    auto literaali = [&](std::size_t u) { return f[u / 3][u % 3]; };
    for (std::size_t u = 0; u < n; ++u) {
        for (std::size_t v = 0; v < n; ++v) {
            bool sama_kolmio = u != v && u / 3 == v / 3;
            bool ristiriita = literaali(u) == -literaali(v);
            g[u][v] = sama_kolmio || ristiriita;
        }
    }
    return g;
}

// Ratkaisu kulkee takaisin: valittujen solmujen literaalit todeksi,
// muut muuttujat mielivaltaisesti epätosiksi.
static std::vector<bool> sijoitus(const Kaava& f, int n,
                                  const std::vector<std::size_t>& joukko)
{
    std::vector<bool> arvo(static_cast<std::size_t>(n) + 1, false);
    for (std::size_t u : joukko) {
        int l = f[u / 3][u % 3];
        arvo[static_cast<std::size_t>(std::abs(l))] = l > 0;
    }
    return arvo;
}
// @loppu reduktio

// @alku haku
// Suurin riippumaton joukko haarautumalla ja karsimalla. Solmujoukot
// ovat 64-bittisiä maskeja (enintään 64 solmua). Yläraja: ehdokkaat
// jaetaan ahneesti klikkeihin, ja kustakin klikistä voi ottaa enintään
// yhden solmun. Tämä yleinen raja tunnistaa reduktion kolmiot.
struct Haku {
    std::vector<std::uint64_t> naapurit;
    std::uint64_t paras = 0;
    int paras_koko = 0;
    long solmuja = 0;   // hakupuun solmuja

    int klikkipeite(std::uint64_t ehdokkaat) const
    {
        int klikkeja = 0;
        while (ehdokkaat != 0) {
            // Klikki: ota pienin solmu ja lisää ahneesti ne, jotka ovat
            // kaikkien jo valittujen naapureita.
            std::uint64_t yhteiset = ehdokkaat;
            while (yhteiset != 0) {
                int v = std::countr_zero(yhteiset);
                ehdokkaat &= ~(std::uint64_t{1} << v);
                yhteiset &= naapurit[static_cast<std::size_t>(v)];
            }
            ++klikkeja;
        }
        return klikkeja;
    }

    void etsi(std::uint64_t ehdokkaat, std::uint64_t valittu, int koko)
    {
        ++solmuja;
        if (koko > paras_koko) {
            paras = valittu;
            paras_koko = koko;
        }
        if (ehdokkaat == 0 || koko + klikkipeite(ehdokkaat) <= paras_koko) {
            return;
        }
        int v = std::countr_zero(ehdokkaat);
        std::uint64_t bitti = std::uint64_t{1} << v;
        // Mukaan: naapurit putoavat ehdokkaista. Pois: vain v putoaa.
        etsi(ehdokkaat & ~bitti & ~naapurit[static_cast<std::size_t>(v)],
             valittu | bitti, koko + 1);
        etsi(ehdokkaat & ~bitti, valittu, koko);
    }
};

static std::vector<std::size_t> suurin_riippumaton(const Verkko& g,
                                                   long& solmuja)
{
    vaadi(!g.empty() && g.size() <= 64, "solmuja oltava 1 ... 64");
    Haku h;
    for (const auto& rivi : g) {
        std::uint64_t maski = 0;
        for (std::size_t v = 0; v < rivi.size(); ++v) {
            maski |= rivi[v] ? std::uint64_t{1} << v : 0;
        }
        h.naapurit.push_back(maski);
    }
    std::uint64_t kaikki = ~std::uint64_t{0} >> (64 - g.size());
    h.etsi(kaikki, 0, 0);
    solmuja += h.solmuja;
    std::vector<std::size_t> joukko;
    for (std::size_t v = 0; v < g.size(); ++v) {
        if ((h.paras >> v) & 1) {
            joukko.push_back(v);
        }
    }
    return joukko;
}
// @loppu haku

int main()
{
    // Pieni kaava ja sen verkko: kirjan kuva piirretään näistä riveistä
    // (kaaviot/tee.py). Solmu 3i + j on lausekkeen i literaali j.
    {
        const Kaava f{{1, 2, -3}, {-1, 2, 3}, {-2, -3, 1}};
        auto g = reduktio(f);
        long solmuja = 0;
        auto joukko = suurin_riippumaton(g, solmuja);
        std::print("kaava:");
        for (const auto& l : f) {
            std::print(" ({} {} {})", l[0], l[1], l[2]);
        }
        std::print("\nristiriitakaaret:");
        for (std::size_t u = 0; u < g.size(); ++u) {
            for (std::size_t v = u + 1; v < g.size(); ++v) {
                if (g[u][v] && u / 3 != v / 3) {
                    std::print(" {}-{}", u, v);
                }
            }
        }
        std::print("\nriippumaton joukko:");
        for (std::size_t u : joukko) {
            std::print(" {}", u);
        }
        auto arvo = sijoitus(f, 3, joukko);
        vaadi(joukko.size() == f.size() && toteuttaa(f, arvo),
              "pienen kaavan reduktio");
        std::println("\nsijoitus: x1={} x2={} x3={}\n", arvo[1] ? 1 : 0,
                     arvo[2] ? 1 : 0, arvo[3] ? 1 : 0);
    }

    // @alku testi
    int toteutuvia = 0;
    long hakusolmuja = 0;
    constexpr int kaavoja = 300;
    for (std::uint64_t siemen = 1; siemen <= kaavoja; ++siemen) {
        Satunnainen s{siemen};
        // Lausekkeita 3n ... 5n: vaikeimmat satunnaiskaavat ovat lähellä
        // suhdetta m / n = 4,26, jossa toteutuvuus putoaa jyrkästi.
        int n = s.valilta(3, 5);
        int m = s.valilta(3 * n, std::min(5 * n, 21));
        Kaava f(static_cast<std::size_t>(m));
        for (auto& lauseke : f) {
            for (int& l : lauseke) {
                l = s.valilta(1, n);
                l = s.alle(2) == 0 ? l : -l;
            }
        }
        auto g = reduktio(f);
        auto paras = suurin_riippumaton(g, hakusolmuja);
        bool sat = toteutuva(f, n);
        vaadi(sat == (paras.size() == f.size()), "reduktio ei säilytä "
                                                 "vastausta");
        if (sat) {
            ++toteutuvia;
            vaadi(toteuttaa(f, sijoitus(f, n, paras)),
                  "joukosta saatu sijoitus ei toteuta kaavaa");
        }
    }
    std::println("{} kaavaa, {} toteutuvaa: reduktio täsmää kaikissa",
                 kaavoja, toteutuvia);
    std::println("riippumattomasta joukosta saatu sijoitus toteuttaa "
                 "kaavan aina");
    std::println("hakupuun solmuja keskimäärin {}", hakusolmuja / kaavoja);
    // @loppu testi
}
