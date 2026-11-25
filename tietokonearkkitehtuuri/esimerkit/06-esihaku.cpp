// Esihaku: seuraavan lohkon esihakija välimuistin edessä. Peräkkäinen
// läpikäynti hyötyy, osoitinjahti ei.
#include <array>
#include <print>
#include <set>
#include <string_view>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/ohjelmat.hpp"
#include "yhteinen/valimuisti.hpp"

// @alku esihaku
struct Tulos { int hudit = 0, esihaut = 0, hyodylliset = 0; };

// Seuraavan lohkon esihakija (next-line prefetcher): aina kun viite
// siirtyy uuteen lohkoon, välimuistiin tuodaan myös sitä seuraava.
Tulos aja(const std::vector<rv::u32>& osoitteet, const rv::VmAsetukset& a,
          bool esihaku) {
    rv::Valimuisti vm(a);
    std::set<rv::u32> odottaa;      // esihaetut lohkot, joita ei ole käytetty
    Tulos t;
    rv::u32 edellinen = ~0u;
    for (const rv::u32 o : osoitteet) {
        const rv::u32 lohko = o / a.lohko;
        const bool osui = vm.viittaa(o, false);
        if (!osui) ++t.hudit;
        if (odottaa.erase(lohko) && osui) ++t.hyodylliset;
        if (esihaku && lohko != edellinen &&
            !vm.viittaa((lohko + 1) * a.lohko, false)) {
            ++t.esihaut;                       // lohko ei ollut jo muistissa
            odottaa.insert(lohko + 1);
        }
        edellinen = lohko;
    }
    return t;
}
// @loppu esihaku

int main() {
    // @alku vertailu
    const std::array<std::pair<std::string_view, std::string_view>, 3>
        testit{{{"summa", ohjelmat::summa}, {"matriisi", ohjelmat::matriisi},
                {"lista", ohjelmat::lista}}};
    const rv::VmAsetukset a{.koko = 256, .lohko = 16, .tiet = 2};
    std::println("{:<10}{:>9}{:>8}{:>10}{:>9}{:>12}", "ohjelma", "viitteet",
                 "hudit", "esihaulla", "esihaut", "hyödylliset");
    for (const auto& [nimi, lahde] : testit) {
        rv::Kone kone(rv::koota(lahde));
        std::vector<rv::u32> osoitteet;
        for (const rv::Tapahtuma& t : kone.aja())
            if (t.lataus || t.talletus) osoitteet.push_back(t.osoite);
        const Tulos ilman = aja(osoitteet, a, false);
        const Tulos kanssa = aja(osoitteet, a, true);
        std::println("{:<10}{:>9}{:>8}{:>10}{:>9}{:>12}", nimi,
                     osoitteet.size(), ilman.hudit, kanssa.hudit,
                     kanssa.esihaut, kanssa.hyodylliset);
    }
    // @loppu vertailu
}
