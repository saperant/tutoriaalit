// Trie eli etuliitepuu: sanojen lisäys, etuliitteen esiintymät ja
// täydennysehdotukset aakkosjärjestyksessä.
#include <algorithm>
#include <array>
#include <optional>
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include "testaus.hpp"

// @alku trie
// Solmut ovat yhdessä taulukossa ja viittaavat toisiinsa indekseillä:
// ei erillisiä varauksia solmua kohden, ja koko puu vapautuu kerralla.
// Aakkosto on a-z; lapsi 0 tarkoittaa "ei lasta", koska juuri on 0.
class Trie {
public:
    Trie() : solmut_(1) {}

    // @alku lisays
    void lisaa(std::string_view sana)
    {
        std::size_t h = 0;
        ++solmut_[h].ohi;
        for (char c : sana) {
            int lapsi = solmut_[h].lapset[indeksi(c)];
            if (lapsi == 0) {
                // emplace_back() voi siirtää taulukon, joten viittausta
                // solmuun ei pidetä sen yli.
                lapsi = static_cast<int>(solmut_.size());
                solmut_[h].lapset[indeksi(c)] = lapsi;
                solmut_.emplace_back();
            }
            h = static_cast<std::size_t>(lapsi);
            ++solmut_[h].ohi;
        }
        ++solmut_[h].paattyy;
    }
    // @loppu lisays

    // Monta lisätyistä sanoista (toistot mukaan lukien) alkaa etuliitteellä.
    int alkaa(std::string_view etuliite) const
    {
        auto h = etsi(etuliite);
        return h ? solmut_[*h].ohi : 0;
    }

    // Enintään k eri sanaa, jotka alkavat etuliitteellä, aakkos-
    // järjestyksessä.
    std::vector<std::string> ehdota(std::string_view etuliite,
                                    std::size_t k) const
    {
        std::vector<std::string> tulos;
        if (auto h = etsi(etuliite)) {
            std::string sana{etuliite};
            keraa(*h, sana, k, tulos);
        }
        return tulos;
    }

    std::size_t solmuja() const { return solmut_.size(); }

private:
    struct Solmu {
        std::array<int, 26> lapset{};
        int ohi = 0;       // sanoja, joiden polku kulkee tästä
        int paattyy = 0;   // sanoja, jotka päättyvät tähän
    };

    static std::size_t indeksi(char c)
    {
        return static_cast<std::size_t>(c - 'a');
    }

    std::optional<std::size_t> etsi(std::string_view s) const
    {
        std::size_t h = 0;
        for (char c : s) {
            int lapsi = solmut_[h].lapset[indeksi(c)];
            if (lapsi == 0) {
                return std::nullopt;
            }
            h = static_cast<std::size_t>(lapsi);
        }
        return h;
    }

    // @alku keraa
    // Syvyyshaku lapsijärjestyksessä tuottaa sanat aakkosjärjestyksessä.
    void keraa(std::size_t h, std::string& sana, std::size_t k,
               std::vector<std::string>& tulos) const
    {
        if (tulos.size() == k) {
            return;
        }
        if (solmut_[h].paattyy > 0) {
            tulos.push_back(sana);
        }
        for (std::size_t c = 0; c < 26; ++c) {
            if (int lapsi = solmut_[h].lapset[c]; lapsi != 0) {
                sana.push_back(static_cast<char>('a' + c));
                keraa(static_cast<std::size_t>(lapsi), sana, k, tulos);
                sana.pop_back();
            }
        }
    }
    // @loppu keraa

    std::vector<Solmu> solmut_;
};
// @loppu trie

int main()
{
    // @alku testi
    // Malli: järjestetty sanalista. Etuliitteellä alkavat sanat ovat
    // peräkkäin, ja niiden väli löytyy binäärihaulla.
    for (std::uint64_t siemen = 1; siemen <= 50; ++siemen) {
        Satunnainen s{siemen};
        auto sana = [&](int pituus) {
            std::string w;
            for (int i = 0; i < pituus; ++i) {
                w += static_cast<char>('a' + s.alle(3));
            }
            return w;
        };
        Trie trie;
        std::vector<std::string> malli;
        for (int i = 0; i < 300; ++i) {
            auto w = sana(s.valilta(0, 6));
            trie.lisaa(w);
            malli.insert(std::ranges::upper_bound(malli, w), w);
        }
        for (int i = 0; i < 300; ++i) {
            auto e = sana(s.valilta(0, 4));
            auto alku = std::ranges::lower_bound(malli, e);
            auto loppu = std::find_if(alku, malli.end(), [&](auto& w) {
                return !w.starts_with(e);
            });
            vaadi(trie.alkaa(e) == loppu - alku, "lukumäärä poikkeaa");
            std::vector<std::string> eri(alku, loppu);
            eri.erase(std::unique(eri.begin(), eri.end()), eri.end());
            eri.resize(std::min<std::size_t>(eri.size(), 5));
            vaadi(trie.ehdota(e, 5) == eri, "ehdotukset poikkeavat");
        }
    }
    std::println("vertailutesti: 50 sanastoa, 15 000 lisäystä ja kyselyä");
    // @loppu testi

    // @alku kaytto
    Trie sanasto;
    for (std::string_view w : {"kala", "kalastaja", "kalastus", "kallio",
                               "kanava", "kansi", "kala", "kalaverkko"}) {
        sanasto.lisaa(w);
    }
    for (std::string_view e : {"kal", "kala", "kan", "ko"}) {
        std::print("{:<5} {} sanaa:", e, sanasto.alkaa(e));
        for (const auto& w : sanasto.ehdota(e, 3)) {
            std::print(" {}", w);
        }
        std::println("");
    }
    std::println("solmuja {}", sanasto.solmuja());
    // @loppu kaytto
}
