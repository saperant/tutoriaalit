// Rekisterin historian linearisoituvuuden tarkistin (Wing ja Gong 1993,
// muistilla tehostettuna kuten Lowe 2017 ja Knossos).
//
// Historia on joukko operaatioita, joilla on alku- ja loppuhetki.
// Historia on linearisoituva, jos jokaiselle operaatiolle voidaan
// valita hetki alun ja lopun väliltä niin, että operaatiot tuossa
// järjestyksessä suoritettuina antavat samat tulokset kuin yksi
// rekisteri.
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <set>
#include <utility>
#include <vector>

// @alku operaatio
struct Operaatio {
    int asiakas;
    bool kirjoitus;
    int arvo;               // kirjoitettu tai luettu arvo
    std::int64_t alku, loppu;
};
constexpr std::int64_t KESKEN = std::numeric_limits<std::int64_t>::max();
// @loppu operaatio

// @alku tarkistin
class Linearisoija {
public:
    Linearisoija(std::vector<Operaatio> h, int alkuarvo)
        : alkuarvo_(alkuarvo) {
        for (auto& o : h)        // keskeneräinen luku ei vaikuta mihinkään
            if (o.kirjoitus || o.loppu != KESKEN) ops_.push_back(o);
    }

    // Palauttaa järjestyksen (indeksit) tai tyhjän, jos sitä ei ole.
    bool tarkista(std::vector<std::size_t>& jarjestys) {
        jarjestys.clear();
        return etsi(0, alkuarvo_, jarjestys);
    }
    const std::vector<Operaatio>& operaatiot() const { return ops_; }

private:
    bool etsi(std::uint64_t tehty, int arvo,
              std::vector<std::size_t>& polku) {
        bool kaikki = true;
        std::int64_t pienin_loppu = KESKEN;
        for (std::size_t i = 0; i < ops_.size(); ++i) {
            if (tehty >> i & 1u) continue;
            if (ops_[i].loppu != KESKEN) kaikki = false;
            pienin_loppu = std::min(pienin_loppu, ops_[i].loppu);
        }
        if (kaikki) return true;          // vain keskeneräisiä jäljellä
        if (!kaynyt_.insert({tehty, arvo}).second) return false;
        for (std::size_t i = 0; i < ops_.size(); ++i) {
            const auto& o = ops_[i];
            // o voi olla seuraava vain, jos mikään tekemätön operaatio
            // ei päättynyt ennen o:n alkua.
            if (tehty >> i & 1u || o.alku > pienin_loppu) continue;
            if (!o.kirjoitus && o.arvo != arvo) continue;
            polku.push_back(i);
            if (etsi(tehty | (std::uint64_t{1} << i),
                     o.kirjoitus ? o.arvo : arvo, polku))
                return true;
            polku.pop_back();
        }
        return false;
    }

    std::vector<Operaatio> ops_;
    int alkuarvo_;
    std::set<std::pair<std::uint64_t, int>> kaynyt_;
};
// @loppu tarkistin

inline bool linearisoituva(const std::vector<Operaatio>& h,
                           int alkuarvo = 0) {
    Linearisoija l(h, alkuarvo);
    std::vector<std::size_t> j;
    return l.tarkista(j);
}
