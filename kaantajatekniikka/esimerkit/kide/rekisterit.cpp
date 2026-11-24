#include "rekisterit.hpp"

#include <algorithm>
#include <ostream>
#include <set>

#include "elavyys.hpp"

namespace kide {

// @alku elinvalit
// Käskyn i operandit luetaan sijainnissa 2i ja tulos kirjoitetaan
// sijainnissa 2i + 1. Siksi arvo, jonka viimeinen käyttö on käskyssä i,
// voi jakaa rekisterin käskyn i tuloksen kanssa: add s1, s1, s2.
std::vector<Elinvali> elinvalit(const IrFunktio& f) {
    Elavyys e = laske_elavyys(f);
    std::size_t n = f.nimet.size();
    std::vector<int> alku(n, -1), loppu(n, -1);
    auto laajenna = [&](Vreg r, int kohta) {
        if (alku[r] < 0 || kohta < alku[r]) alku[r] = kohta;
        loppu[r] = std::max(loppu[r], kohta);
    };
    for (Vreg p = 0; p < f.parametreja; ++p) laajenna(p, 0);
    int i = 0;
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        int ensimmainen = 2 * i;
        for (const Kasky& k : f.lohkot[b].kaskyt) {
            for (Vreg r : k.lahteet) laajenna(r, 2 * i);
            if (k.kohde >= 0) laajenna(k.kohde, 2 * i + 1);
            ++i;
        }
        int viimeinen = 2 * i - 1;
        for (std::size_t r = 0; r < n; ++r) {
            if (e.sisaan[b][r]) laajenna(static_cast<Vreg>(r), ensimmainen);
            if (e.ulos[b][r]) laajenna(static_cast<Vreg>(r), viimeinen);
        }
    }
    std::vector<Elinvali> valit;
    for (std::size_t r = 0; r < n; ++r) {
        if (alku[r] >= 0) {
            valit.push_back({static_cast<Vreg>(r), alku[r], loppu[r]});
        }
    }
    std::ranges::sort(valit, [](const Elinvali& a, const Elinvali& b) {
        return a.alku != b.alku ? a.alku < b.alku : a.rekisteri < b.rekisteri;
    });
    return valit;
}
// @loppu elinvalit

// @alku pinoon
Varaus varaa_pinoon(const IrFunktio& f) {
    Varaus v;
    v.paikat.resize(f.nimet.size());
    for (const Elinvali& e : elinvalit(f)) {
        v.paikat[e.rekisteri].pinopaikka = v.pinopaikkoja++;
    }
    return v;
}
// @loppu pinoon

// @alku lineaarinen
// Poletton ja Sarkarin lineaarinen pyyhkäisy (1999): välit käydään
// alkukohdan mukaan, ja päättyneiden välien rekisterit vapautetaan.
Varaus varaa_lineaarisesti(const IrFunktio& f, int rekistereita) {
    Varaus v;
    v.paikat.resize(f.nimet.size());
    std::set<int> vapaat;
    for (int r = 1; r <= rekistereita; ++r) vapaat.insert(r);
    std::vector<Elinvali> aktiiviset;    // rekisterissä olevat välit
    auto vie_pinoon = [&](Vreg r) {
        v.paikat[r] = {.pinopaikka = v.pinopaikkoja++};
    };
    for (const Elinvali& e : elinvalit(f)) {
        std::erase_if(aktiiviset, [&](const Elinvali& a) {
            if (a.loppu >= e.alku) return false;
            vapaat.insert(v.paikat[a.rekisteri].rekisteri);
            return true;
        });
        if (!vapaat.empty()) {
            v.paikat[e.rekisteri].rekisteri = *vapaat.begin();
            vapaat.erase(vapaat.begin());
            aktiiviset.push_back(e);
            continue;
        }
        // Ei vapaata rekisteriä: pinoon menee se väli, joka päättyy
        // viimeisenä, koska se varaisi rekisteriä pisimpään.
        auto pisin = std::ranges::max_element(
            aktiiviset, {}, [](const Elinvali& a) { return a.loppu; });
        if (pisin != aktiiviset.end() && pisin->loppu > e.loppu) {
            v.paikat[e.rekisteri].rekisteri =
                v.paikat[pisin->rekisteri].rekisteri;
            vie_pinoon(pisin->rekisteri);
            *pisin = e;
        } else {
            vie_pinoon(e.rekisteri);
        }
    }
    std::set<int> kaytetyt;
    for (const Paikka& p : v.paikat) {
        if (p.rekisteri > 0) kaytetyt.insert(p.rekisteri);
    }
    v.kaytetyt.assign(kaytetyt.begin(), kaytetyt.end());
    return v;
}
// @loppu lineaarinen

void tulosta_varaus(const IrFunktio& f, const Varaus& v, std::ostream& u) {
    u << "fn " << f.nimi << '\n';
    for (const Elinvali& e : elinvalit(f)) {
        auto tasaa = [&](const std::string& s, std::size_t leveys) {
            u << s << std::string(s.size() < leveys ? leveys - s.size() : 1,
                                  ' ');
        };
        u << "  ";
        tasaa(rekisteri(f, e.rekisteri), 8);
        tasaa("[" + std::to_string(e.alku) + ", " + std::to_string(e.loppu)
                  + "]",
              10);
        const Paikka& p = v.paikat[e.rekisteri];
        if (p.rekisteri > 0) {
            u << 's' << p.rekisteri << '\n';
        } else {
            u << "pino " << p.pinopaikka << '\n';
        }
    }
}

}  // namespace kide
