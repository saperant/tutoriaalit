// Kirjoituspolitiikat ja kaksitasoisen hierarkian keskimääräinen
// muistiviive (AMAT) simuloiduista hutisuhteista.
#include <array>
#include <print>
#include <string_view>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/ohjelmat.hpp"
#include "yhteinen/valimuisti.hpp"

struct Viite { rv::u32 osoite; bool kirjoitus; };

std::vector<Viite> viitteet(std::string_view lahde) {
    rv::Kone kone(rv::koota(lahde));
    std::vector<Viite> v;
    for (const rv::Tapahtuma& t : kone.aja())
        if (t.lataus || t.talletus) v.push_back({t.osoite, t.talletus});
    return v;
}

int main() {
    const std::array<std::pair<std::string_view, std::string_view>, 3>
        testit{{{"summa", ohjelmat::summa}, {"kupla", ohjelmat::kupla},
                {"matriisi", ohjelmat::matriisi}}};
    // @alku politiikat
    // Liikenne muistiin tavuina: luetut lohkot, takaisin kirjoitetut
    // likaiset lohkot ja läpikirjoitetut sanat. 256 B, 16 B lohkot, 2-tie.
    std::println("{:<9} {:>7} {:>5}  {:>9} {:>9} {:>9}", "ohjelma",
                 "viitteet", "kirj", "WB+WA", "WT+WA", "WT+noWA");
    for (const auto& [nimi, lahde] : testit) {
        const std::vector<Viite> v = viitteet(lahde);
        long kirjoitukset = 0;
        for (const Viite& x : v) kirjoitukset += x.kirjoitus;
        std::print("{:<9} {:>7} {:>5} ", nimi, v.size(), kirjoitukset);
        for (const auto& [wb, wa] : {std::pair{true, true}, {false, true},
                                     {false, false}}) {
            rv::Valimuisti vm({.koko = 256, .lohko = 16, .tiet = 2,
                               .takaisinkirjoitus = wb,
                               .kirjoitusvaraus = wa});
            for (const Viite& x : v) vm.viittaa(x.osoite, x.kirjoitus);
            const rv::VmTilastot& t = vm.tilastot();
            const auto tavut = 16 * (t.luetut_lohkot + t.kirjoitetut_lohkot)
                               + 4 * t.kirjoitetut_sanat;
            std::print(" {:>9}", tavut);
        }
        std::println();
    }
    // @loppu politiikat
    // @alku amat
    // L1 256 B suora, L2 2 KiB 4-tie. Viiveet jaksoina: L1 1, L2 10,
    // keskusmuisti 100. AMAT = t1 + h1 (t2 + h2 tm), h2 paikallinen.
    std::println("\n{:<9} {:>7} {:>7} {:>8}", "ohjelma", "h1 (%)",
                 "h2 (%)", "AMAT");
    for (const auto& [nimi, lahde] : testit) {
        rv::Valimuisti l1({.koko = 256, .lohko = 16, .tiet = 1});
        rv::Valimuisti l2({.koko = 2048, .lohko = 32, .tiet = 4});
        for (const Viite& x : viitteet(lahde))
            if (!l1.viittaa(x.osoite, x.kirjoitus))
                l2.viittaa(x.osoite, x.kirjoitus);
        const double h1 = 1 - l1.tilastot().osumasuhde();
        const double h2 = 1 - l2.tilastot().osumasuhde();
        std::println("{:<9} {:>7.1f} {:>7.1f} {:>8.2f}", nimi, 100 * h1,
                     100 * h2, 1 + h1 * (10 + h2 * 100));
    }
    // @loppu amat
}
