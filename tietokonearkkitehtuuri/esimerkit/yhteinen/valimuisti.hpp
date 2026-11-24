// Parametrisoitava välimuistimalli: koko, lohkon koko, assosiatiivisuus,
// korvauspolitiikka ja kirjoituspolitiikka. Malli laskee osumat ja hudit
// sekä muistiin menevän liikenteen; dataa se ei tallenna.
#pragma once
#include <cstdint>
#include <format>
#include <set>
#include <string>
#include <vector>

namespace rv {

enum class Korvaus { LRU, FIFO, Satunnainen };

// @alku asetukset
struct VmAsetukset {
    std::uint32_t koko = 1024;          // tavua
    std::uint32_t lohko = 16;           // tavua
    std::uint32_t tiet = 1;             // 1 = suora kuvaus
    Korvaus korvaus = Korvaus::LRU;
    bool takaisinkirjoitus = true;      // false = läpikirjoitus
    bool kirjoitusvaraus = true;        // kirjoitushuti tuo lohkon
};

struct VmTilastot {
    std::uint64_t viitteet = 0, hudit = 0;
    std::uint64_t luetut_lohkot = 0;     // muistista välimuistiin
    std::uint64_t kirjoitetut_lohkot = 0;  // likaiset lohkot muistiin
    std::uint64_t kirjoitetut_sanat = 0;   // läpikirjoitukset
    double osumasuhde() const {
        return viitteet == 0 ? 0.0
                             : 1.0 - static_cast<double>(hudit) /
                                         static_cast<double>(viitteet);
    }
};
// @loppu asetukset

// @alku valimuisti
class Valimuisti {
public:
    explicit Valimuisti(const VmAsetukset& a)
        : a_(a), joukot_(a.koko / a.lohko / a.tiet),
          rivit_(a.koko / a.lohko) {}

    // Palauttaa true, jos viite osui välimuistiin.
    bool viittaa(std::uint32_t osoite, bool kirjoitus) {
        ++t_.viitteet;
        ++aika_;
        const std::uint32_t lohko = osoite / a_.lohko;
        const std::uint32_t joukko = lohko % joukot_;
        const std::uint32_t tagi = lohko / joukot_;
        Rivi* joukon_alku = &rivit_[joukko * a_.tiet];
        for (std::uint32_t i = 0; i < a_.tiet; ++i) {
            Rivi& r = joukon_alku[i];
            if (r.kelvollinen && r.tagi == tagi) {
                r.kaytetty = aika_;
                kirjoita(r, kirjoitus);
                return true;
            }
        }
        ++t_.hudit;
        if (kirjoitus && !a_.kirjoitusvaraus) {
            ++t_.kirjoitetut_sanat;  // kirjoitus suoraan muistiin
            return false;
        }
        Rivi& uhri = valitse(joukon_alku);
        if (uhri.kelvollinen && uhri.likainen) ++t_.kirjoitetut_lohkot;
        uhri = {true, false, tagi, aika_, aika_};
        ++t_.luetut_lohkot;
        kirjoita(uhri, kirjoitus);
        return false;
    }

    const VmTilastot& tilastot() const { return t_; }

private:
    struct Rivi {
        bool kelvollinen = false, likainen = false;
        std::uint32_t tagi = 0;
        std::uint64_t kaytetty = 0, tuotu = 0;
    };

    void kirjoita(Rivi& r, bool kirjoitus) {
        if (!kirjoitus) return;
        if (a_.takaisinkirjoitus) r.likainen = true;
        else ++t_.kirjoitetut_sanat;
    }

    Rivi& valitse(Rivi* joukko) {
        for (std::uint32_t i = 0; i < a_.tiet; ++i)
            if (!joukko[i].kelvollinen) return joukko[i];
        if (a_.korvaus == Korvaus::Satunnainen) {
            satunnainen_ = satunnainen_ * 1103515245u + 12345u;
            return joukko[(satunnainen_ >> 16) % a_.tiet];
        }
        Rivi* uhri = joukko;
        for (std::uint32_t i = 1; i < a_.tiet; ++i) {
            const Rivi& r = joukko[i];
            const bool vanhempi = a_.korvaus == Korvaus::LRU
                                      ? r.kaytetty < uhri->kaytetty
                                      : r.tuotu < uhri->tuotu;
            if (vanhempi) uhri = &joukko[i];
        }
        return *uhri;
    }

    VmAsetukset a_;
    std::uint32_t joukot_;
    std::vector<Rivi> rivit_;
    VmTilastot t_;
    std::uint64_t aika_ = 0;
    std::uint32_t satunnainen_ = 1;
};
// @loppu valimuisti

// @alku kolme_c
// Hutien luokittelu 3C-mallilla: pakolliset (lohkoon viitataan
// ensimmäistä kertaa), kapasiteettihudit (myös samankokoinen täysin
// assosiatiivinen LRU-välimuisti hutisi) ja ristiriitahudit (loput).
struct KolmeC { std::uint64_t pakolliset, kapasiteetti, ristiriita; };

inline KolmeC luokittele(const std::vector<std::uint32_t>& osoitteet,
                         const VmAsetukset& a) {
    Valimuisti oikea(a);
    VmAsetukset ta = a;
    ta.tiet = a.koko / a.lohko;  // yksi joukko
    ta.korvaus = Korvaus::LRU;
    Valimuisti taysi(ta);
    std::set<std::uint32_t> nahdyt;
    for (std::uint32_t o : osoitteet) {
        nahdyt.insert(o / a.lohko);
        oikea.viittaa(o, false);
        taysi.viittaa(o, false);
    }
    const std::uint64_t p = nahdyt.size();
    const std::uint64_t t = taysi.tilastot().hudit;
    const std::uint64_t h = oikea.tilastot().hudit;
    return {p, t - p, h > t ? h - t : 0};
}
// @loppu kolme_c

}  // namespace rv
