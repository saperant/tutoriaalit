// Suffiksitaulukko ja LCP-taulukko: kaikki merkkijonon loppuosat
// järjestyksessä sekä naapurien yhteisten etuliitteiden pituudet.
#include <algorithm>
#include <numeric>
#include <print>
#include <set>
#include <string>
#include <string_view>
#include <vector>

#include "testaus.hpp"

// @alku taulukko
// Etuliitteiden tuplaus: kierroksella k suffiksit on järjestetty
// 2^k ensimmäisen merkin mukaan, ja luokka[i] kertoo suffiksin i
// järjestysnumeron. Seuraava kierros järjestää parit
// (luokka[i], luokka[i + 2^k]). O(n log^2 n) std::sortilla; s ei tyhjä.
static std::vector<int> suffiksitaulukko(std::string_view s)
{
    auto n = static_cast<int>(s.size());
    std::vector<int> sa(s.size()), luokka(s.size()), uusi(s.size());
    std::iota(sa.begin(), sa.end(), 0);
    for (std::size_t i = 0; i < s.size(); ++i) {
        luokka[i] = static_cast<unsigned char>(s[i]);
    }
    for (int k = 1;; k *= 2) {
        // Avain: (oma luokka, luokka k merkkiä myöhemmin tai -1).
        auto avain = [&](int i) {
            int toinen = i + k < n ? luokka[static_cast<std::size_t>(i + k)]
                                   : -1;
            return std::pair{luokka[static_cast<std::size_t>(i)], toinen};
        };
        std::ranges::sort(sa, {}, avain);
        uusi[static_cast<std::size_t>(sa[0])] = 0;
        for (std::size_t j = 1; j < sa.size(); ++j) {
            bool eri = avain(sa[j - 1]) < avain(sa[j]);
            uusi[static_cast<std::size_t>(sa[j])] =
                uusi[static_cast<std::size_t>(sa[j - 1])] + (eri ? 1 : 0);
        }
        luokka.swap(uusi);
        if (luokka[static_cast<std::size_t>(sa.back())] == n - 1) {
            return sa;   // kaikki luokat eri: järjestys on valmis
        }
    }
}
// @loppu taulukko

// @alku lcp
// Kasain algoritmi: lcp[j] = suffiksien sa[j - 1] ja sa[j] yhteisen
// etuliitteen pituus. Kun siirrytään suffiksista i suffiksiin i + 1,
// yhteinen pituus pienenee enintään yhdellä, joten työ on O(n).
static std::vector<int> lcp_taulukko(std::string_view s,
                                     const std::vector<int>& sa)
{
    std::vector<int> sija(s.size()), lcp(s.size(), 0);
    for (std::size_t j = 0; j < sa.size(); ++j) {
        sija[static_cast<std::size_t>(sa[j])] = static_cast<int>(j);
    }
    std::size_t h = 0;
    for (std::size_t i = 0; i < s.size(); ++i) {
        auto j = static_cast<std::size_t>(sija[i]);
        if (j == 0) {
            h = 0;
            continue;
        }
        auto edellinen = static_cast<std::size_t>(sa[j - 1]);
        while (i + h < s.size() && edellinen + h < s.size()
               && s[i + h] == s[edellinen + h]) {
            ++h;
        }
        lcp[j] = static_cast<int>(h);
        if (h > 0) {
            --h;
        }
    }
    return lcp;
}
// @loppu lcp

// @alku kaytto
// Hahmon esiintymät ovat suffiksitaulukossa yhtenäinen väli: ne
// suffiksit, joiden etuliite hahmo on. Kaksi binäärihakua, O(m log n).
static int esiintymia(std::string_view s, const std::vector<int>& sa,
                      std::string_view hahmo)
{
    auto etuliite = [&](int i) {
        return s.substr(static_cast<std::size_t>(i), hahmo.size());
    };
    auto alku = std::ranges::lower_bound(sa, hahmo, {}, etuliite);
    auto loppu = std::ranges::upper_bound(sa, hahmo, {}, etuliite);
    return static_cast<int>(loppu - alku);
}

// Pisin vähintään kahdesti esiintyvä osajono: suurin LCP-arvo.
static std::string_view pisin_toistuva(std::string_view s,
                                       const std::vector<int>& sa,
                                       const std::vector<int>& lcp)
{
    auto j = static_cast<std::size_t>(std::ranges::max_element(lcp)
                                      - lcp.begin());
    return s.substr(static_cast<std::size_t>(sa[j]),
                    static_cast<std::size_t>(lcp[j]));
}

// Eri osajonojen määrä: jokainen suffiksi tuo pituutensa verran
// etuliitteitä, joista lcp on jo nähty edellisessä suffiksissa.
static long eri_osajonoja(std::size_t n, const std::vector<int>& lcp)
{
    auto kaikki = static_cast<long>(n * (n + 1) / 2);
    return kaikki - std::accumulate(lcp.begin(), lcp.end(), 0L);
}
// @loppu kaytto

int main()
{
    // @alku banaani
    std::string_view sana = "banaani";
    auto sa = suffiksitaulukko(sana);
    auto lcp = lcp_taulukko(sana, sa);
    for (std::size_t j = 0; j < sa.size(); ++j) {
        std::println("{} {} {}", sa[j], lcp[j],
                     sana.substr(static_cast<std::size_t>(sa[j])));
    }
    // @loppu banaani

    // @alku testi
    for (std::uint64_t siemen = 1; siemen <= 300; ++siemen) {
        Satunnainen s{siemen};
        std::string t;
        for (int i = s.valilta(1, 40); i > 0; --i) {
            t += static_cast<char>('a' + s.alle(siemen % 3 + 1));
        }
        // Malli: suffiksit järjestetään vertaamalla niitä suoraan.
        std::vector<int> malli(t.size());
        std::iota(malli.begin(), malli.end(), 0);
        std::string_view tv = t;
        std::ranges::sort(malli, {}, [&](int i) {
            return tv.substr(static_cast<std::size_t>(i));
        });
        auto sa2 = suffiksitaulukko(t);
        vaadi(sa2 == malli, "suffiksitaulukko poikkeaa");
        auto lcp2 = lcp_taulukko(t, sa2);
        std::set<std::string_view> osat;
        for (std::size_t i = 0; i < t.size(); ++i) {
            for (std::size_t m = 1; i + m <= t.size(); ++m) {
                osat.insert(tv.substr(i, m));
            }
        }
        vaadi(eri_osajonoja(t.size(), lcp2) == static_cast<long>(osat.size()),
              "eri osajonojen määrä poikkeaa");
        std::string_view hahmo = tv.substr(s.alle(t.size()), 2);
        int suora = 0;
        for (auto p = tv.find(hahmo); p != tv.npos;
             p = tv.find(hahmo, p + 1)) {
            ++suora;
        }
        vaadi(esiintymia(t, sa2, hahmo) == suora, "esiintymät poikkeavat");
    }
    std::println("vertailutesti: 300 merkkijonoa, 0 eroa");
    // @loppu testi

    // @alku teksti
    std::string_view teksti =
        "kalastaja kalasti kalaa kalasaaresta ja kalasatamasta";
    sa = suffiksitaulukko(teksti);
    lcp = lcp_taulukko(teksti, sa);
    std::println("pisin toistuva: \"{}\"", pisin_toistuva(teksti, sa, lcp));
    std::println("\"kala\" {} kertaa, \"sta\" {} kertaa",
                 esiintymia(teksti, sa, "kala"),
                 esiintymia(teksti, sa, "sta"));
    std::println("eri osajonoja {}", eri_osajonoja(teksti.size(), lcp));
    // @loppu teksti
}
