// A*-reitinhaku ruudukossa. Sama funktio on Dijkstran algoritmi, kun
// heuristiikaksi annetaan nolla.
#pragma once
#include <climits>
#include <cstddef>
#include <cstdlib>
#include <queue>
#include <span>
#include <string_view>
#include <vector>

// @alku kartta
struct Ruutu {
    int x, y;
    bool operator==(const Ruutu&) const = default;
};

// Kartta merkkeinä: '#' on este, '~' suota (askel maksaa 3), muu
// tavallista maata (askel maksaa 1).
struct Kartta {
    std::span<const std::string_view> rivit;

    int leveys() const { return static_cast<int>(rivit[0].size()); }
    int korkeus() const { return static_cast<int>(rivit.size()); }

    char merkki(Ruutu r) const {
        if (r.x < 0 || r.y < 0 || r.x >= leveys() || r.y >= korkeus()) {
            return '#';
        }
        return rivit[static_cast<std::size_t>(r.y)]
                    [static_cast<std::size_t>(r.x)];
    }
    // Askeleen hinta ruutuun; 0 tarkoittaa, ettei ruutuun pääse.
    int hinta(Ruutu r) const {
        const char m = merkki(r);
        return m == '#' ? 0 : m == '~' ? 3 : 1;
    }
};
// @loppu kartta

// @alku heuristiikka
// Arvio jäljellä olevasta hinnasta. Arvio ei saa olla todellista
// suurempi (sallittu heuristiikka), muuten reitti ei ole halvin.
// Neljän suunnan ruudukossa Manhattan-etäisyys täyttää ehdon.
using Heuristiikka = int (*)(Ruutu, Ruutu);

inline int manhattan(Ruutu a, Ruutu b) {
    return std::abs(a.x - b.x) + std::abs(a.y - b.y);
}
inline int nolla(Ruutu, Ruutu) { return 0; }
// @loppu heuristiikka

// @alku haku
struct Reitti {
    std::vector<Ruutu> polku;     // alusta maaliin; tyhjä = ei reittiä
    int hinta = 0;
    std::vector<Ruutu> tutkitut;  // ruudut käsittelyjärjestyksessä
};

inline Reitti hae_reitti(const Kartta& k, Ruutu alku, Ruutu maali,
                         Heuristiikka h) {
    struct Avoin {
        int f, g, jarjestys;  // f = g + h: arvio koko reitin hinnasta
        Ruutu r;
    };
    // Jonon kärkeen pienin f. Tasatilanteessa suurin g (pisimmälle
    // edennyt) ja sitten uusin: järjestys on täysin määrätty, joten
    // tulos on sama joka ajolla ja joka kääntäjällä.
    auto huonompi = [](const Avoin& a, const Avoin& b) {
        if (a.f != b.f) {
            return a.f > b.f;
        }
        if (a.g != b.g) {
            return a.g < b.g;
        }
        return a.jarjestys < b.jarjestys;
    };
    std::priority_queue<Avoin, std::vector<Avoin>, decltype(huonompi)>
        avoimet(huonompi);

    const int w = k.leveys();
    const auto n = static_cast<std::size_t>(w * k.korkeus());
    auto i = [w](Ruutu r) { return static_cast<std::size_t>(r.y * w + r.x); };
    std::vector<int> g(n, INT_MAX);        // halvin tunnettu hinta alusta
    std::vector<Ruutu> mista(n, {-1, -1});  // mistä ruutuun tultiin
    std::vector<bool> valmis(n, false);

    Reitti tulos;
    int laskuri = 0;
    g[i(alku)] = 0;
    avoimet.push({h(alku, maali), 0, laskuri, alku});
    while (!avoimet.empty()) {
        const Avoin nyt = avoimet.top();
        avoimet.pop();
        if (valmis[i(nyt.r)]) {
            continue;  // ruutu käsiteltiin jo halvemmalla hinnalla
        }
        valmis[i(nyt.r)] = true;
        tulos.tutkitut.push_back(nyt.r);
        if (nyt.r == maali) {
            tulos.hinta = nyt.g;
            for (Ruutu r = maali; r != Ruutu{-1, -1}; r = mista[i(r)]) {
                tulos.polku.insert(tulos.polku.begin(), r);
            }
            return tulos;
        }
        for (const Ruutu d : {Ruutu{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
            const Ruutu s{nyt.r.x + d.x, nyt.r.y + d.y};
            const int askel = k.hinta(s);
            if (askel == 0 || nyt.g + askel >= g[i(s)]) {
                continue;  // este, tai ruutuun osataan jo halvemmalla
            }
            g[i(s)] = nyt.g + askel;
            mista[i(s)] = nyt.r;
            avoimet.push({g[i(s)] + h(s, maali), g[i(s)], ++laskuri, s});
        }
    }
    return tulos;  // jono tyhjeni: maaliin ei pääse
}
// @loppu haku
