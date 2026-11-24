// Kaksijakoinen paritus: lisäyspolut (Kuhn), sama virtauksena ja
// Königin lauseen pienin solmupeite.
#include <algorithm>
#include <array>
#include <bit>
#include <print>
#include <string_view>
#include <vector>

#include "testaus.hpp"
#include "virtaus.hpp"

using Vierus = std::vector<std::vector<int>>;   // vasen -> oikeat

// @alku kuhn
// Kuhnin algoritmi: jokaiselle vasemmalle solmulle etsitään lisäyspolku
// syvyyshaulla. Polku vuorottelee parittomia ja paritettuja kaaria ja
// päättyy vapaaseen oikeaan solmuun; sen kääntäminen kasvattaa
// paritusta yhdellä. O(V E).
struct Paritus {
    std::vector<int> pari_vasen, pari_oikea;   // -1 = vapaa
    int koko = 0;
};

static bool lisayspolku(const Vierus& g, int u, std::vector<bool>& kayty,
                        Paritus& p)
{
    for (int v : g[static_cast<std::size_t>(u)]) {
        auto vi = static_cast<std::size_t>(v);
        if (kayty[vi]) {
            continue;
        }
        kayty[vi] = true;
        int nykyinen = p.pari_oikea[vi];
        if (nykyinen < 0 || lisayspolku(g, nykyinen, kayty, p)) {
            p.pari_oikea[vi] = u;
            p.pari_vasen[static_cast<std::size_t>(u)] = v;
            return true;
        }
    }
    return false;
}

static Paritus kuhn(const Vierus& g, int oikeita)
{
    Paritus p{std::vector(g.size(), -1),
              std::vector(static_cast<std::size_t>(oikeita), -1), 0};
    for (std::size_t u = 0; u < g.size(); ++u) {
        std::vector<bool> kayty(static_cast<std::size_t>(oikeita), false);
        if (lisayspolku(g, static_cast<int>(u), kayty, p)) {
            ++p.koko;
        }
    }
    return p;
}
// @loppu kuhn

// @alku virtauksena
// Sama tehtävä virtauksena: lähde -> vasen (1), vasen -> oikea (1),
// oikea -> nielu (1). Kokonaislukukapasiteeteilla suurin virta on
// kokonaislukuinen, joten se on paritus.
static long virtauksena(const Vierus& g, int oikeita)
{
    auto vasempia = static_cast<int>(g.size());
    int s = vasempia + oikeita, t = s + 1;
    Virtausverkko verkko{t + 1};
    for (int u = 0; u < vasempia; ++u) {
        verkko.lisaa_kaari(s, u, 1);
        for (int v : g[static_cast<std::size_t>(u)]) {
            verkko.lisaa_kaari(u, vasempia + v, 1);
        }
    }
    for (int v = 0; v < oikeita; ++v) {
        verkko.lisaa_kaari(vasempia + v, t, 1);
    }
    return verkko.dinic(s, t);
}
// @loppu virtauksena

// @alku konig
// Königin lause: kaksijakoisessa verkossa pienin solmupeite on yhtä
// suuri kuin suurin paritus. Z = solmut, jotka saavutetaan vapaista
// vasemmista solmuista vuorottelevilla poluilla; peite on
// (vasen \ Z) + (oikea ja Z).
static std::pair<std::vector<int>, std::vector<int>>
peite(const Vierus& g, const Paritus& p)
{
    std::vector<bool> z_vasen(g.size(), false),
        z_oikea(p.pari_oikea.size(), false);
    std::vector<int> pino;
    for (std::size_t u = 0; u < g.size(); ++u) {
        if (p.pari_vasen[u] < 0) {
            z_vasen[u] = true;
            pino.push_back(static_cast<int>(u));
        }
    }
    while (!pino.empty()) {
        auto u = static_cast<std::size_t>(pino.back());
        pino.pop_back();
        for (int v : g[u]) {   // pariton kaari vasemmalta oikealle
            auto vi = static_cast<std::size_t>(v);
            if (!z_oikea[vi]) {
                z_oikea[vi] = true;
                int w = p.pari_oikea[vi];   // paritettu kaari takaisin
                if (w >= 0 && !z_vasen[static_cast<std::size_t>(w)]) {
                    z_vasen[static_cast<std::size_t>(w)] = true;
                    pino.push_back(w);
                }
            }
        }
    }
    std::vector<int> vasen, oikea;
    for (std::size_t u = 0; u < g.size(); ++u) {
        if (!z_vasen[u]) {
            vasen.push_back(static_cast<int>(u));
        }
    }
    for (std::size_t v = 0; v < z_oikea.size(); ++v) {
        if (z_oikea[v]) {
            oikea.push_back(static_cast<int>(v));
        }
    }
    return {vasen, oikea};
}
// @loppu konig

// Malli: pienin solmupeite käymällä läpi kaikki solmujoukot.
static int pienin_peite(const Vierus& g, int oikeita)
{
    auto n = static_cast<int>(g.size()) + oikeita;
    int paras = n;
    for (unsigned maski = 0; maski < (1u << n); ++maski) {
        bool peittaa = true;
        for (std::size_t u = 0; u < g.size() && peittaa; ++u) {
            for (int v : g[u]) {
                unsigned vb = 1u << (static_cast<int>(g.size()) + v);
                if (!((maski >> u) & 1) && !(maski & vb)) {
                    peittaa = false;
                }
            }
        }
        if (peittaa) {
            paras = std::min(paras, std::popcount(maski));
        }
    }
    return paras;
}

int main()
{
    // @alku testi
    for (std::uint64_t siemen = 1; siemen <= 200; ++siemen) {
        Satunnainen s{siemen};
        int vasempia = s.valilta(1, 6), oikeita = s.valilta(1, 6);
        Vierus g(static_cast<std::size_t>(vasempia));
        for (auto& naapurit : g) {
            for (int v = 0; v < oikeita; ++v) {
                if (s.alle(3) == 0) {
                    naapurit.push_back(v);
                }
            }
        }
        auto p = kuhn(g, oikeita);
        vaadi(virtauksena(g, oikeita) == p.koko, "virtaus poikkeaa");
        auto [pv, po] = peite(g, p);
        vaadi(static_cast<int>(pv.size() + po.size()) == p.koko,
              "peitteen koko ei ole parituksen koko");
        for (std::size_t u = 0; u < g.size(); ++u) {
            for (int v : g[u]) {
                vaadi(std::ranges::contains(pv, static_cast<int>(u))
                          || std::ranges::contains(po, v),
                      "kaari jää peittämättä");
            }
        }
        vaadi(pienin_peite(g, oikeita) == p.koko, "Königin lause");
    }
    std::println("vertailutesti: 200 verkkoa, paritus = virtaus = peite");
    // @loppu testi

    // @alku kaytto
    constexpr std::array<std::string_view, 5> opiskelija{
        "Aino", "Eero", "Iida", "Onni", "Ukko"};
    constexpr std::array<std::string_view, 4> aihe{
        "kääntäjä", "tietokanta", "verkko", "grafiikka"};
    const Vierus toiveet{{0, 1}, {0}, {1, 2}, {0, 2}, {1}};
    auto p = kuhn(toiveet, 4);
    std::println("paritus {} / {}:", p.koko, opiskelija.size());
    for (std::size_t u = 0; u < toiveet.size(); ++u) {
        int v = p.pari_vasen[u];
        std::println("  {} -> {}", opiskelija[u],
                     v < 0 ? "ei aihetta"
                           : aihe[static_cast<std::size_t>(v)]);
    }
    auto [pv, po] = peite(toiveet, p);
    std::print("peite (selittää, miksi enempää ei saada):");
    for (int u : pv) {
        std::print(" {}", opiskelija[static_cast<std::size_t>(u)]);
    }
    for (int v : po) {
        std::print(" {}", aihe[static_cast<std::size_t>(v)]);
    }
    std::println("");
    // @loppu kaytto
}
