// Merkkijonohaku: suora haku, Knuthin-Morrisin-Prattin algoritmi ja
// Z-algoritmi. Vertailuja lasketaan, ja tuloksia verrataan toisiinsa.
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include "testaus.hpp"

static long vertailuja = 0;

static bool sama(char a, char b)
{
    ++vertailuja;
    return a == b;
}

// @alku suora
// Kokeillaan jokaista alkukohtaa: pahimmillaan O(n m).
static std::vector<int> suora(std::string_view teksti,
                              std::string_view hahmo)
{
    std::vector<int> osumat;
    for (std::size_t i = 0; i + hahmo.size() <= teksti.size(); ++i) {
        std::size_t j = 0;
        while (j < hahmo.size() && sama(teksti[i + j], hahmo[j])) {
            ++j;
        }
        if (j == hahmo.size()) {
            osumat.push_back(static_cast<int>(i));
        }
    }
    return osumat;
}
// @loppu suora

// @alku vikafunktio
// vika[j] = pisimmän sellaisen hahmon[0, j] aidon etuliitteen pituus,
// joka on myös sen loppuliite. Kun vertailu epäonnistuu kohdassa j,
// haku jatkuu kohdasta vika[j - 1] eikä tekstissä palata taaksepäin.
static std::vector<int> vikafunktio(std::string_view hahmo)
{
    std::vector<int> vika(hahmo.size(), 0);
    std::size_t k = 0;
    for (std::size_t j = 1; j < hahmo.size(); ++j) {
        for (;;) {
            if (sama(hahmo[j], hahmo[k])) {
                ++k;
                break;
            }
            if (k == 0) {
                break;
            }
            k = static_cast<std::size_t>(vika[k - 1]);
        }
        vika[j] = static_cast<int>(k);
    }
    return vika;
}

// Tekstin merkki luetaan kerran; jokainen epäonnistuminen lyhentää
// osumaa, joten vertailuja on enintään 2n (vikafunktiolle 2m).
static std::vector<int> kmp(std::string_view teksti, std::string_view hahmo)
{
    std::vector<int> osumat;
    auto vika = vikafunktio(hahmo);
    std::size_t k = 0;
    for (std::size_t i = 0; i < teksti.size(); ++i) {
        for (;;) {
            if (sama(teksti[i], hahmo[k])) {
                ++k;
                break;
            }
            if (k == 0) {
                break;
            }
            k = static_cast<std::size_t>(vika[k - 1]);   // lyhyempi osuma
        }
        if (k == hahmo.size()) {
            osumat.push_back(static_cast<int>(i + 1 - k));
            k = static_cast<std::size_t>(vika[k - 1]);
        }
    }
    return osumat;
}
// @loppu vikafunktio

// @alku z
// z[i] = pisimmän sellaisen merkkijonon pituus, joka alkaa kohdasta i
// ja on myös s:n etuliite. [l, r) on oikeimmalle ulottuva löydetty
// osuma; sen sisällä z[i] saadaan jo lasketusta z[i - l]:stä.
static std::vector<int> z_funktio(std::string_view s)
{
    std::vector<int> z(s.size(), 0);
    std::size_t l = 0, r = 0;
    for (std::size_t i = 1; i < s.size(); ++i) {
        std::size_t k = 0;
        if (i < r) {
            k = std::min(r - i, static_cast<std::size_t>(z[i - l]));
        }
        while (i + k < s.size() && sama(s[k], s[i + k])) {
            ++k;
        }
        z[i] = static_cast<int>(k);
        if (i + k > r) {
            l = i;
            r = i + k;
        }
    }
    return z;
}

// Haku: Z-funktio jonolle hahmo + erotin + teksti. Erotin ei saa
// esiintyä kummassakaan.
static std::vector<int> z_haku(std::string_view teksti,
                               std::string_view hahmo)
{
    std::string s{hahmo};
    s += '\0';
    s += teksti;
    auto z = z_funktio(s);
    std::vector<int> osumat;
    for (std::size_t i = hahmo.size() + 1; i < s.size(); ++i) {
        if (static_cast<std::size_t>(z[i]) == hahmo.size()) {
            osumat.push_back(static_cast<int>(i - hahmo.size() - 1));
        }
    }
    return osumat;
}
// @loppu z

int main()
{
    // @alku vika
    for (std::string_view h : {"ababaca", "aabaaab", "abcabd"}) {
        std::print("vika({}) =", h);
        for (int v : vikafunktio(h)) {
            std::print(" {}", v);
        }
        std::println("");
    }
    // @loppu vika

    // @alku testi
    // Pienet aakkostot tuottavat paljon osittaisia osumia, joissa
    // virheet näkyvät.
    for (std::uint64_t siemen = 1; siemen <= 500; ++siemen) {
        Satunnainen s{siemen};
        auto merkki = [&] {
            return static_cast<char>('a' + s.alle(siemen % 3 + 1));
        };
        std::string teksti, hahmo;
        for (int i = s.valilta(0, 60); i > 0; --i) {
            teksti += merkki();
        }
        for (int i = s.valilta(1, 6); i > 0; --i) {
            hahmo += merkki();
        }
        auto odotettu = suora(teksti, hahmo);
        vaadi(kmp(teksti, hahmo) == odotettu, "KMP poikkeaa");
        vaadi(z_haku(teksti, hahmo) == odotettu, "Z-haku poikkeaa");
    }
    std::println("vertailutesti: 500 satunnaista tekstiä, 0 eroa");
    // @loppu testi

    // @alku pahin
    // Pahin tapaus suoralle haulle: teksti a^n ja hahmo a^(m-1) b.
    std::string teksti(100000, 'a');
    std::string hahmo = std::string(999, 'a') + "b";
    using Haku = std::vector<int> (*)(std::string_view, std::string_view);
    for (auto [nimi, haku] : {std::pair<const char*, Haku>{"suora", suora},
                              {"KMP", kmp}, {"Z", z_haku}}) {
        vertailuja = 0;
        auto osumat = haku(teksti, hahmo);
        std::println("{:<6} {:>10} vertailua, {} osumaa", nimi, vertailuja,
                     osumat.size());
    }
    // @loppu pahin
}
