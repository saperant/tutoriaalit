// Loogiset kellot: Lamportin kello, vektorikello ja hybridikello.
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

// @alku lamport
class Lamport {
public:
    std::int64_t tapahtuma() { return ++aika_; }          // paikallinen
    std::int64_t lahetys() { return ++aika_; }            // leima viestiin
    std::int64_t vastaanotto(std::int64_t leima) {
        aika_ = std::max(aika_, leima) + 1;
        return aika_;
    }
    std::int64_t nyt() const { return aika_; }
private:
    std::int64_t aika_ = 0;
};
// @loppu lamport

// @alku vektori
enum class Suhde { Sama, Ennen, Jalkeen, Samanaikainen };

class Vektorikello {
public:
    explicit Vektorikello(std::size_t solmuja) : v_(solmuja, 0) {}

    void tapahtuma(std::size_t oma) { ++v_[oma]; }
    void yhdista(const Vektorikello& muu) {           // vastaanotossa
        for (std::size_t i = 0; i < v_.size(); ++i)
            v_[i] = std::max(v_[i], muu.v_[i]);
    }

    // Tapahtuiko tämä ennen toista, sen jälkeen vai samanaikaisesti?
    Suhde vertaa(const Vektorikello& muu) const {
        bool pienempi = false, suurempi = false;
        for (std::size_t i = 0; i < v_.size(); ++i) {
            if (v_[i] < muu.v_[i]) pienempi = true;
            if (v_[i] > muu.v_[i]) suurempi = true;
        }
        if (pienempi && suurempi) return Suhde::Samanaikainen;
        if (pienempi) return Suhde::Ennen;
        if (suurempi) return Suhde::Jalkeen;
        return Suhde::Sama;
    }

    std::string teksti() const {
        std::string s = "[";
        for (std::size_t i = 0; i < v_.size(); ++i)
            s += (i ? "," : "") + std::to_string(v_[i]);
        return s + "]";
    }
private:
    std::vector<std::int64_t> v_;
};
// @loppu vektori

// @alku hlc
// Hybridikello (Kulkarni ym. 2014): leima (l, c), jossa l seuraa
// fyysistä kelloa ja c erottaa tapahtumat, joilla on sama l.
struct Hlc {
    std::int64_t l = 0, c = 0;
    bool operator<(const Hlc& o) const {
        return l != o.l ? l < o.l : c < o.c;
    }
};

class Hybridikello {
public:
    Hlc tapahtuma(std::int64_t fyysinen) {      // myös lähetys
        if (fyysinen > h_.l) {
            h_ = {fyysinen, 0};
        } else {
            ++h_.c;
        }
        return h_;
    }
    Hlc vastaanotto(std::int64_t fyysinen, Hlc m) {
        std::int64_t l = std::max({h_.l, m.l, fyysinen});
        std::int64_t c = 0;
        if (l == h_.l && l == m.l) c = std::max(h_.c, m.c) + 1;
        else if (l == h_.l) c = h_.c + 1;
        else if (l == m.l) c = m.c + 1;
        h_ = {l, c};
        return h_;
    }
private:
    Hlc h_;
};
// @loppu hlc
