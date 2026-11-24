// Kauppamatkustajan ongelma tason pisteillä: tarkka Heldin-Karpin
// dynaaminen ohjelmointi pienille syötteille sekä heuristiikat
// (lähin naapuri, virittävän puun kierto ja 2-opt).
#include <algorithm>
#include <cmath>
#include <limits>
#include <print>
#include <vector>

#include "testaus.hpp"

using Etaisyydet = std::vector<std::vector<int>>;
using Kierros = std::vector<int>;

static int pituus(const Etaisyydet& d, const Kierros& k)
{
    int summa = 0;
    for (std::size_t i = 0; i < k.size(); ++i) {
        auto a = static_cast<std::size_t>(k[i]);
        auto b = static_cast<std::size_t>(k[(i + 1) % k.size()]);
        summa += d[a][b];
    }
    return summa;
}

// @alku tarkka
// Held-Karp: paras[S][v] = lyhin polku solmusta 0 joukon S kautta
// solmuun v. O(2^n n^2) aikaa ja O(2^n n) muistia: n = 20 on jo raskas,
// mutta raaka läpikäynti (n - 1)! / 2 kierrosta on paljon pahempi.
static int held_karp(const Etaisyydet& d)
{
    auto n = d.size();
    constexpr int aareton = std::numeric_limits<int>::max() / 2;
    std::vector<std::vector<int>> paras(std::size_t{1} << n,
                                        std::vector<int>(n, aareton));
    paras[1][0] = 0;
    for (std::size_t s = 1; s < (std::size_t{1} << n); s += 2) {
        for (std::size_t v = 0; v < n; ++v) {
            if (paras[s][v] == aareton) {
                continue;
            }
            for (std::size_t w = 0; w < n; ++w) {
                if (!((s >> w) & 1)) {
                    auto t = s | (std::size_t{1} << w);
                    paras[t][w] = std::min(paras[t][w],
                                           paras[s][v] + d[v][w]);
                }
            }
        }
    }
    int tulos = aareton;
    for (std::size_t v = 1; v < n; ++v) {
        tulos = std::min(tulos, paras.back()[v] + d[v][0]);
    }
    return tulos;
}
// @loppu tarkka

// @alku heuristiikat
// Lähin naapuri: aina lähimpään käymättömään. Nopea, mutta viimeiset
// siirtymät joutuvat usein kulkemaan pitkiä matkoja.
static Kierros lahin_naapuri(const Etaisyydet& d)
{
    std::vector<bool> kayty(d.size(), false);
    Kierros k{0};
    kayty[0] = true;
    while (k.size() < d.size()) {
        auto u = static_cast<std::size_t>(k.back());
        std::size_t paras = 0;
        int lyhin = std::numeric_limits<int>::max();
        for (std::size_t v = 0; v < d.size(); ++v) {
            if (!kayty[v] && d[u][v] < lyhin) {
                lyhin = d[u][v];
                paras = v;
            }
        }
        kayty[paras] = true;
        k.push_back(static_cast<int>(paras));
    }
    return k;
}

// Virittävän puun kierto: kierros ilman yhtä kaarta on virittävä puu,
// joten MST <= OPT. Puun esijärjestys kulkee jokaisen kaaren
// enintään kahdesti, ja kolmioepäyhtälön ansiosta oikopolut eivät
// pidennä: kierros <= 2 MST <= 2 OPT.
static Kierros puukierros(const Etaisyydet& d, int& mst)
{
    auto n = d.size();
    std::vector<int> etaisyys(n, std::numeric_limits<int>::max());
    std::vector<std::size_t> vanhempi(n, 0);
    std::vector<bool> puussa(n, false);
    std::vector<std::vector<std::size_t>> lapset(n);
    etaisyys[0] = 0;
    mst = 0;
    for (std::size_t kierros = 0; kierros < n; ++kierros) {   // Prim O(n^2)
        std::size_t u = n;
        for (std::size_t v = 0; v < n; ++v) {
            if (!puussa[v] && (u == n || etaisyys[v] < etaisyys[u])) {
                u = v;
            }
        }
        puussa[u] = true;
        mst += etaisyys[u];
        if (u != 0) {
            lapset[vanhempi[u]].push_back(u);
        }
        for (std::size_t v = 0; v < n; ++v) {
            if (!puussa[v] && d[u][v] < etaisyys[v]) {
                etaisyys[v] = d[u][v];
                vanhempi[v] = u;
            }
        }
    }
    Kierros k;
    std::vector<std::size_t> pino{0};
    while (!pino.empty()) {
        auto u = pino.back();
        pino.pop_back();
        k.push_back(static_cast<int>(u));
        pino.insert(pino.end(), lapset[u].rbegin(), lapset[u].rend());
    }
    return k;
}

// @alku kaksiopt
// 2-opt: jos kaarten (a, b) ja (c, e) vaihtaminen kaariin (a, c) ja
// (b, e) lyhentää kierrosta, väli b ... c käännetään. Toistetaan,
// kunnes parannusta ei löydy (paikallinen optimi).
static void kaksi_opt(const Etaisyydet& d, Kierros& k)
{
    auto n = k.size();
    auto e = [&](std::size_t i, std::size_t j) {
        auto a = static_cast<std::size_t>(k[i]);
        return d[a][static_cast<std::size_t>(k[j])];
    };
    for (bool parani = true; parani;) {
        parani = false;
        for (std::size_t i = 0; i + 2 < n; ++i) {
            for (std::size_t j = i + 2; j < n; ++j) {
                std::size_t j1 = (j + 1) % n;
                if (j1 == i) {
                    continue;
                }
                if (e(i, j) + e(i + 1, j1) < e(i, i + 1) + e(j, j1)) {
                    auto alku = k.begin() + static_cast<std::ptrdiff_t>(i);
                    std::reverse(alku + 1, alku + static_cast<std::ptrdiff_t>(
                                                      j - i + 1));
                    parani = true;
                }
            }
        }
    }
}
// @loppu kaksiopt
// @loppu heuristiikat

int main()
{
    // @alku vertailu
    // 30 satunnaista 11 kaupungin karttaa, koordinaatit 0 ... 999,
    // etäisyys pyöristetty euklidinen (kuten TSPLIBin EUC_2D).
    struct Tulos {
        const char* nimi;
        double summa = 0, huonoin = 0;
    };
    Tulos tulokset[] = {{"lähin naapuri"}, {"puukierros"},
                        {"lähin naapuri + 2-opt"}};
    Satunnainen s{17};
    constexpr int karttoja = 30;
    for (int kartta = 0; kartta < karttoja; ++kartta) {
        constexpr std::size_t n = 11;
        std::vector<std::pair<int, int>> p(n);
        for (auto& [x, y] : p) {
            x = s.valilta(0, 999);
            y = s.valilta(0, 999);
        }
        Etaisyydet d(n, std::vector<int>(n));
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = 0; j < n; ++j) {
                double dx = p[i].first - p[j].first;
                double dy = p[i].second - p[j].second;
                d[i][j] = static_cast<int>(std::lround(std::hypot(dx, dy)));
            }
        }
        int opt = held_karp(d);
        int mst = 0;
        auto nn = lahin_naapuri(d);
        auto puu = puukierros(d, mst);
        vaadi(mst <= opt && pituus(d, puu) <= 2 * mst, "puuraja ei päde");
        auto parannettu = nn;
        kaksi_opt(d, parannettu);
        int pituudet[] = {pituus(d, nn), pituus(d, puu),
                          pituus(d, parannettu)};
        for (std::size_t i = 0; i < 3; ++i) {
            vaadi(pituudet[i] >= opt, "heuristiikka voitti optimin");
            double suhde = static_cast<double>(pituudet[i]) / opt;
            tulokset[i].summa += suhde;
            tulokset[i].huonoin = std::max(tulokset[i].huonoin, suhde);
        }
    }
    std::println("{:<22} {:>12} {:>8}", "menetelmä", "keskimäärin",
                 "huonoin");
    for (const auto& t : tulokset) {
        std::println("{:<22} {:12.3f} {:8.3f}", t.nimi, t.summa / karttoja,
                     t.huonoin);
    }
    // @loppu vertailu
}
