// Staattinen törmäysmaailma: kolmiot ja niiden BVH.
#pragma once
#include "bvh.hpp"
#include "mallit.hpp"

#include <vector>

// @alku maailma
class Maailma {
public:
    void lisaa(const Verkko& verkko, const Mat4& malli = yksikko()) {
        for (const Kolmio& k : kolmioiksi(verkko, malli))
            kolmiot_.push_back(k);
    }
    // Kutsutaan, kun kaikki verkot on lisätty.
    void valmis() {
        laatikot_.clear();
        for (const Kolmio& k : kolmiot_) laatikot_.push_back(ymparys(k));
        puu_ = rakenna_bvh(laatikot_);
    }
    // Kutsuu funktiota jokaiselle kolmiolle, jonka laatikko osuu alueeseen.
    template <typename F>
    void alueella(const Laatikko& alue, F&& f) const {
        kay_lapi(
            puu_, [&](const Laatikko& l) { return leikkaavat(l, alue); },
            [&](int i) {
                if (leikkaavat(laatikot_[i], alue)) f(kolmiot_[i]);
            });
    }
    Osuma sade(const Sade& s) const {
        return sade_bvh(puu_, s,
                        [&](int i) { return sade_kolmio(s, kolmiot_[i]); });
    }
    const std::vector<Kolmio>& kolmiot() const { return kolmiot_; }

private:
    std::vector<Kolmio> kolmiot_;
    std::vector<Laatikko> laatikot_;
    Bvh puu_;
};
// @loppu maailma
