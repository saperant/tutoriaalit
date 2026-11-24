// Rabinin-Karpin haku liukuvalla polynomihajautuksella. Hajautusarvon
// täsmääminen on vasta ehdokas: osuma varmistetaan vertaamalla.
#include <bit>
#include <cstdint>
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include "testaus.hpp"

// @alku hajautus
// Laskenta modulo Mersennen alkuluku p = 2^61 - 1. Kantaluku arvotaan,
// joten hyökkääjä ei voi etukäteen rakentaa törmääviä syötteitä: kahden
// eri m-merkkisen jonon törmäyksen todennäköisyys on enintään m / p.
__extension__ using U128 = unsigned __int128;

constexpr std::uint64_t P = (std::uint64_t{1} << 61) - 1;

static std::uint64_t kerro(std::uint64_t a, std::uint64_t b)
{
    U128 t = static_cast<U128>(a) * b;
    std::uint64_t tulos = static_cast<std::uint64_t>(t & P)
                          + static_cast<std::uint64_t>(t >> 61);
    return tulos >= P ? tulos - P : tulos;
}

static std::uint64_t summaa(std::uint64_t a, std::uint64_t b)
{
    std::uint64_t s = a + b;
    return s >= P ? s - P : s;
}

// @alku rk
struct Haku {
    std::vector<int> osumat;
    int ehdokkaita = 0;   // hajautusarvo täsmäsi
};

static Haku rabin_karp(std::string_view teksti, std::string_view hahmo,
                       std::uint64_t kanta)
{
    Haku tulos;
    std::size_t m = hahmo.size();
    if (m > teksti.size()) {
        return tulos;
    }
    // h(s) = s[0] k^(m-1) + s[1] k^(m-2) + ... + s[m-1]  (mod p)
    std::uint64_t hh = 0, ht = 0, korkein = 1;
    for (std::size_t i = 0; i < m; ++i) {
        hh = summaa(kerro(hh, kanta), static_cast<unsigned char>(hahmo[i]));
        ht = summaa(kerro(ht, kanta), static_cast<unsigned char>(teksti[i]));
        if (i + 1 < m) {
            korkein = kerro(korkein, kanta);
        }
    }
    for (std::size_t i = 0;; ++i) {
        if (ht == hh) {
            ++tulos.ehdokkaita;
            if (teksti.substr(i, m) == hahmo) {
                tulos.osumat.push_back(static_cast<int>(i));
            }
        }
        if (i + m == teksti.size()) {
            break;
        }
        // Ikkuna siirtyy: vanhin merkki pois, uusi perään.
        auto pois = kerro(korkein, static_cast<unsigned char>(teksti[i]));
        ht = summaa(ht, P - pois);
        ht = summaa(kerro(ht, kanta),
                    static_cast<unsigned char>(teksti[i + m]));
    }
    return tulos;
}
// @loppu rk
// @loppu hajautus

// @alku thue
// Hajautus modulo 2^64 (etumerkitön ylivuoto) on nopea, mutta Thuen-
// Morsen jono ja sen komplementti törmäävät millä tahansa parittomalla
// kantaluvulla, kun pituus on 2^11. Parillinen kanta on vielä huonompi:
// merkit siirtyvät sanan yläpäästä pois.
static std::uint64_t hajautus64(std::string_view s, std::uint64_t kanta)
{
    std::uint64_t h = 0;
    for (char c : s) {
        h = h * kanta + static_cast<unsigned char>(c);
    }
    return h;
}

static std::uint64_t hajautus_p(std::string_view s, std::uint64_t kanta)
{
    std::uint64_t h = 0;
    for (char c : s) {
        h = summaa(kerro(h, kanta), static_cast<unsigned char>(c));
    }
    return h;
}

static std::string thue_morse(int pituus, bool komplementti)
{
    std::string s;
    for (int i = 0; i < pituus; ++i) {
        bool bitti = (std::popcount(static_cast<unsigned>(i)) % 2 == 1)
                     != komplementti;
        s += bitti ? 'b' : 'a';
    }
    return s;
}
// @loppu thue

int main()
{
    Satunnainen s{8};
    std::uint64_t kanta = 256 + s.alle(P - 256);

    // @alku testi
    int ehdokkaita = 0, osumia = 0;
    for (std::uint64_t siemen = 1; siemen <= 300; ++siemen) {
        Satunnainen t{siemen};
        std::string teksti, hahmo;
        for (int i = t.valilta(0, 200); i > 0; --i) {
            teksti += static_cast<char>('a' + t.alle(2));
        }
        for (int i = t.valilta(1, 8); i > 0; --i) {
            hahmo += static_cast<char>('a' + t.alle(2));
        }
        std::vector<int> odotettu;
        for (auto p = teksti.find(hahmo); p != std::string::npos;
             p = teksti.find(hahmo, p + 1)) {
            odotettu.push_back(static_cast<int>(p));
        }
        auto haku = rabin_karp(teksti, hahmo, kanta);
        vaadi(haku.osumat == odotettu, "osumat poikkeavat");
        ehdokkaita += haku.ehdokkaita;
        osumia += static_cast<int>(odotettu.size());
    }
    std::println("vertailutesti: 300 tekstiä, {} osumaa, {} turhaa "
                 "ehdokasta", osumia, ehdokkaita - osumia);
    // @loppu testi

    // @alku tormays
    auto a = thue_morse(2048, false), b = thue_morse(2048, true);
    const std::uint64_t kannat[] = {31, 131, 1000003, s.seuraava() | 1};
    for (std::uint64_t k : kannat) {
        std::println("kanta {:20}: mod 2^64 {}, mod 2^61-1 {}", k,
                     hajautus64(a, k) == hajautus64(b, k) ? "törmää"
                                                          : "eroaa",
                     hajautus_p(a, k % P) == hajautus_p(b, k % P)
                         ? "törmää"
                         : "eroaa");
    }
    // @loppu tormays
}
