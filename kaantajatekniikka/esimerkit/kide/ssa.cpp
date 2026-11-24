#include "ssa.hpp"

#include <algorithm>
#include <functional>
#include <ostream>
#include <set>

#include "elavyys.hpp"

namespace kide {

namespace {

// Lohkot käänteisessä jälkijärjestyksessä (reverse postorder): lohko
// tulee ennen seuraajiaan, paitsi silmukan paluukaarissa.
std::vector<int> kaanteinen_jalkijarjestys(const IrFunktio& f) {
    std::vector<int> tulos;
    std::vector<bool> nahty(f.lohkot.size());
    std::function<void(int)> kay = [&](int b) {
        nahty[b] = true;
        for (int s : f.lohkot[b].seuraajat) {
            if (!nahty[s]) kay(s);
        }
        tulos.push_back(b);
    };
    kay(0);
    std::reverse(tulos.begin(), tulos.end());
    return tulos;
}

}  // namespace

// @alku dominoijat
// Cooperin, Harveyn ja Kennedyn iteratiivinen algoritmi.
std::vector<int> dominoijat(const IrFunktio& f) {
    std::vector<int> jarjestys = kaanteinen_jalkijarjestys(f);
    std::vector<int> numero(f.lohkot.size());
    for (std::size_t i = 0; i < jarjestys.size(); ++i) {
        numero[jarjestys[i]] = static_cast<int>(i);
    }
    std::vector<int> idom(f.lohkot.size(), -1);
    idom[0] = 0;
    // Kahden dominoijan lähin yhteinen esi-isä dominanssipuussa.
    auto leikkaus = [&](int a, int b) {
        while (a != b) {
            while (numero[a] > numero[b]) a = idom[a];
            while (numero[b] > numero[a]) b = idom[b];
        }
        return a;
    };
    for (bool muuttui = true; muuttui;) {
        muuttui = false;
        for (int b : jarjestys) {
            if (b == 0) continue;
            int uusi = -1;
            for (int e : f.lohkot[b].edeltajat) {
                if (idom[e] < 0) continue;          // ei vielä käsitelty
                uusi = uusi < 0 ? e : leikkaus(e, uusi);
            }
            if (idom[b] != uusi) {
                idom[b] = uusi;
                muuttui = true;
            }
        }
    }
    return idom;
}
// @loppu dominoijat

namespace {

// @alku raja
// Dominanssiraja DF(b): lohkot, joissa b:n dominanssi päättyy. Niissä
// b:ssä tehty määrittely kohtaa muita polkuja, ja tarvitaan phi.
std::vector<std::set<int>> dominanssirajat(const IrFunktio& f,
                                           const std::vector<int>& idom) {
    std::vector<std::set<int>> df(f.lohkot.size());
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        const auto& edeltajat = f.lohkot[b].edeltajat;
        if (edeltajat.size() < 2) continue;
        for (int e : edeltajat) {
            for (int r = e; r != idom[b]; r = idom[r]) {
                df[r].insert(static_cast<int>(b));
            }
        }
    }
    return df;
}
// @loppu raja

class SsaMuunnin {
public:
    explicit SsaMuunnin(const IrFunktio& f) : f_(f), tulos_(f) {}
    IrFunktio muunna();

private:
    void lisaa_phit();
    void nimea(int b);
    Vreg uusi_versio(Vreg alkup);

    const IrFunktio& f_;
    IrFunktio tulos_;
    std::vector<int> idom_;
    std::vector<std::vector<int>> lapset_;     // dominanssipuu
    std::vector<std::vector<Vreg>> pinot_;     // alkup. -> versiot
    std::vector<int> versioita_;
    std::vector<int> maarittelyja_;
};

// @alku phit
void SsaMuunnin::lisaa_phit() {
    auto df = dominanssirajat(f_, idom_);
    Elavyys e = laske_elavyys(f_);
    std::size_t n = f_.nimet.size();
    std::vector<std::set<int>> maaritellaan(n);
    for (Vreg p = 0; p < f_.parametreja; ++p) maaritellaan[p].insert(0);
    for (std::size_t b = 0; b < f_.lohkot.size(); ++b) {
        for (const Kasky& k : f_.lohkot[b].kaskyt) {
            if (k.kohde >= 0) {
                maaritellaan[k.kohde].insert(static_cast<int>(b));
            }
        }
    }
    for (std::size_t r = 0; r < n; ++r) {
        std::vector<int> tyolista(maaritellaan[r].begin(),
                                  maaritellaan[r].end());
        std::set<int> phi;
        while (!tyolista.empty()) {
            int b = tyolista.back();
            tyolista.pop_back();
            for (int d : df[b]) {
                // Karsittu SSA: phi vain, jos arvo on elävä lohkon alussa.
                if (phi.count(d) || !e.sisaan[d][r]) continue;
                phi.insert(d);
                auto& kaskyt = tulos_.lohkot[d].kaskyt;
                Kasky k{.op = Op::Phi, .kohde = static_cast<Vreg>(r)};
                k.lahteet.assign(f_.lohkot[d].edeltajat.size(),
                                 static_cast<Vreg>(r));
                k.lohkot = f_.lohkot[d].edeltajat;
                kaskyt.insert(kaskyt.begin(), k);
                // Phi on itsekin määrittely, joka voi vaatia uusia phejä.
                if (!maaritellaan[r].count(d)) tyolista.push_back(d);
            }
        }
    }
}
// @loppu phit

Vreg SsaMuunnin::uusi_versio(Vreg alkup) {
    // Yhden kerran määritellyt väliaikaiset säilyttävät nimensä.
    std::string nimi = f_.nimet[alkup];
    if (nimi[0] != '%' || maarittelyja_[alkup] > 1) {
        nimi += "." + std::to_string(versioita_[alkup]++);
    }
    tulos_.nimet.push_back(nimi);
    Vreg uusi = static_cast<Vreg>(tulos_.nimet.size()) - 1;
    pinot_[alkup].push_back(uusi);
    return uusi;
}

// @alku nimea
// Uudelleennimeäminen kulkee dominanssipuun syvyyshakuna: kunkin
// rekisterin pinon päällä on sen viimeisin dominoiva määrittely.
void SsaMuunnin::nimea(int b) {
    std::vector<Vreg> lisatyt;
    auto nykyinen = [&](Vreg r) {
        return pinot_[r].empty() ? -1 : pinot_[r].back();
    };
    for (Kasky& k : tulos_.lohkot[b].kaskyt) {
        if (k.op != Op::Phi) {
            for (Vreg& r : k.lahteet) r = nykyinen(r);
        }
        if (k.kohde >= 0) {
            lisatyt.push_back(k.kohde);
            k.kohde = uusi_versio(k.kohde);
        }
    }
    // Seuraajien phi-käskyt saavat tämän lohkon kautta tulevan arvon.
    std::set<int> seuraajat(f_.lohkot[b].seuraajat.begin(),
                            f_.lohkot[b].seuraajat.end());
    for (int s : seuraajat) {
        for (Kasky& k : tulos_.lohkot[s].kaskyt) {
            if (k.op != Op::Phi) break;
            for (std::size_t i = 0; i < k.lohkot.size(); ++i) {
                if (k.lohkot[i] == b) k.lahteet[i] = nykyinen(k.lahteet[i]);
            }
        }
    }
    for (int c : lapset_[b]) nimea(c);
    for (Vreg r : lisatyt) pinot_[r].pop_back();
}
// @loppu nimea

IrFunktio SsaMuunnin::muunna() {
    idom_ = dominoijat(f_);
    lapset_.assign(f_.lohkot.size(), {});
    for (std::size_t b = 1; b < f_.lohkot.size(); ++b) {
        lapset_[idom_[b]].push_back(static_cast<int>(b));
    }
    lisaa_phit();
    std::size_t n = f_.nimet.size();
    pinot_.assign(n, {});
    versioita_.assign(n, 0);
    maarittelyja_.assign(n, 0);
    for (const Peruslohko& l : tulos_.lohkot) {
        for (const Kasky& k : l.kaskyt) {
            if (k.kohde >= 0) ++maarittelyja_[k.kohde];
        }
    }
    // Uudet rekisterit numeroidaan alkuperäisten perään; parametrien
    // ensimmäiset versiot ovat edelleen 0 .. n-1.
    tulos_.nimet.clear();
    for (Vreg p = 0; p < f_.parametreja; ++p) uusi_versio(p);
    nimea(0);
    return std::move(tulos_);
}

}  // namespace

IrFunktio ssa_muotoon(const IrFunktio& f) { return SsaMuunnin(f).muunna(); }

void tulosta_dominanssi(const IrFunktio& f, std::ostream& u) {
    auto idom = dominoijat(f);
    auto df = dominanssirajat(f, idom);
    u << "fn " << f.nimi << '\n';
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        u << "  L" << b << "  idom ";
        if (b == 0) {
            u << "-";
        } else {
            u << 'L' << idom[b];
        }
        u << "  DF {";
        bool eka = true;
        for (int d : df[b]) {
            u << (eka ? "" : " ") << 'L' << d;
            eka = false;
        }
        u << "}\n";
    }
}

}  // namespace kide
