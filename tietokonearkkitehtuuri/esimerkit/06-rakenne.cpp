// Välimuistin rakenne: osoitteen jako kenttiin, lyhyen viitejonon
// osumat ja hudit sekä koon ja lohkokoon vaikutus osumasuhteeseen.
#include <bit>
#include <print>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/ohjelmat.hpp"
#include "yhteinen/valimuisti.hpp"

int main() {
    // @alku kentat
    // 256 tavua, 16 tavun lohkot, suora kuvaus: 16 riviä.
    const rv::VmAsetukset a{.koko = 256, .lohko = 16, .tiet = 1};
    const unsigned siirtyma = std::countr_zero(a.lohko);
    const unsigned indeksi = std::countr_zero(a.koko / a.lohko / a.tiet);
    std::println("siirtymä {} bittiä, indeksi {} bittiä, tagi {} bittiä",
                 siirtyma, indeksi, 32 - siirtyma - indeksi);
    rv::Valimuisti vm(a);
    for (const rv::u32 o : {0x100u, 0x104u, 0x10cu, 0x110u, 0x200u,
                            0x104u, 0x204u, 0x100u}) {
        const rv::u32 ind = o >> siirtyma & ((1u << indeksi) - 1);
        const bool osui = vm.viittaa(o, false);
        std::println("0x{:03x}: tagi 0x{:x} indeksi {:2} siirtymä {:2} {}",
                     o, o >> (siirtyma + indeksi), ind,
                     o & (a.lohko - 1), osui ? "osuma" : "huti");
    }
    // @loppu kentat
    // @alku koko
    // Matriisitulon datamuistiviitteet koon ja lohkokoon funktiona.
    rv::Kone kone(rv::koota(ohjelmat::matriisi));
    std::vector<std::pair<rv::u32, bool>> viitteet;
    for (const rv::Tapahtuma& t : kone.aja())
        if (t.lataus || t.talletus)
            viitteet.emplace_back(t.osoite, t.talletus);
    std::println("\n{} viitettä; osumasuhde (%), suora kuvaus",
                 viitteet.size());
    std::print("{:>8}", "koko");
    for (rv::u32 lohko = 4; lohko <= 128; lohko *= 2)
        std::print("{:>7}", std::format("{} B", lohko));
    std::println();
    for (rv::u32 koko = 256; koko <= 4096; koko *= 2) {
        std::print("{:>8}", std::format("{} B", koko));
        for (rv::u32 lohko = 4; lohko <= 128; lohko *= 2) {
            rv::Valimuisti v({.koko = koko, .lohko = lohko});
            for (const auto& [o, kirjoitus] : viitteet)
                v.viittaa(o, kirjoitus);
            std::print("{:>7.1f}", 100 * v.tilastot().osumasuhde());
        }
        std::println();
    }
    // @loppu koko
}
