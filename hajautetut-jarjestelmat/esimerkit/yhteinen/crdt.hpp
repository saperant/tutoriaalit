// Tilapohjaiset CRDT:t: kasvava laskuri, kaksisuuntainen laskuri ja
// havainnoiva poistojoukko (OR-Set). Yhdistäminen on vaihdannainen,
// liitännäinen ja idempotentti, joten replikat lähentyvät samaan
// tilaan riippumatta siitä, missä järjestyksessä ja kuinka monta kertaa
// tilat vaihdetaan.
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

// @alku glaskuri
class GLaskuri {
public:
    explicit GLaskuri(std::size_t replikoita = 0) : v_(replikoita, 0) {}
    void kasvata(std::size_t oma, std::int64_t n = 1) { v_[oma] += n; }
    std::int64_t arvo() const {
        std::int64_t s = 0;
        for (auto x : v_) s += x;
        return s;
    }
    void yhdista(const GLaskuri& muu) {
        for (std::size_t i = 0; i < v_.size(); ++i)
            v_[i] = std::max(v_[i], muu.v_[i]);
    }
    bool operator==(const GLaskuri&) const = default;
private:
    std::vector<std::int64_t> v_;   // kunkin replikan oma osuus
};
// @loppu glaskuri

// @alku pnlaskuri
class PNLaskuri {
public:
    explicit PNLaskuri(std::size_t replikoita = 0)
        : plus_(replikoita), miinus_(replikoita) {}
    void kasvata(std::size_t oma) { plus_.kasvata(oma); }
    void vahenna(std::size_t oma) { miinus_.kasvata(oma); }
    std::int64_t arvo() const { return plus_.arvo() - miinus_.arvo(); }
    void yhdista(const PNLaskuri& muu) {
        plus_.yhdista(muu.plus_);
        miinus_.yhdista(muu.miinus_);
    }
    bool operator==(const PNLaskuri&) const = default;
private:
    GLaskuri plus_, miinus_;
};
// @loppu pnlaskuri

// @alku orjoukko
// Jokainen lisäys saa yksilöllisen tunnisteen (replika, laskuri).
// Poisto poistaa ne tunnisteet, jotka poistaja on nähnyt; samanaikainen
// lisäys toisessa replikassa jää voimaan ("lisäys voittaa").
class ORJoukko {
public:
    using Tunniste = std::pair<std::size_t, std::int64_t>;

    void lisaa(std::size_t oma, const std::string& x) {
        lisatyt_[x].insert({oma, ++laskuri_});
    }
    void poista(const std::string& x) {
        auto it = lisatyt_.find(x);
        if (it == lisatyt_.end()) return;
        for (const auto& t : it->second) poistetut_.insert(t);
    }
    bool sisaltaa(const std::string& x) const {
        auto it = lisatyt_.find(x);
        if (it == lisatyt_.end()) return false;
        for (const auto& t : it->second)
            if (!poistetut_.contains(t)) return true;
        return false;
    }
    std::vector<std::string> alkiot() const {
        std::vector<std::string> v;
        for (const auto& [x, t] : lisatyt_)
            if (sisaltaa(x)) v.push_back(x);
        return v;
    }
    void yhdista(const ORJoukko& muu) {
        for (const auto& [x, t] : muu.lisatyt_)
            lisatyt_[x].insert(t.begin(), t.end());
        poistetut_.insert(muu.poistetut_.begin(), muu.poistetut_.end());
        laskuri_ = std::max(laskuri_, muu.laskuri_);
    }
    bool operator==(const ORJoukko& o) const {
        return alkiot() == o.alkiot();
    }
private:
    std::map<std::string, std::set<Tunniste>> lisatyt_;
    std::set<Tunniste> poistetut_;       // hautakivet
    std::int64_t laskuri_ = 0;
};
// @loppu orjoukko
