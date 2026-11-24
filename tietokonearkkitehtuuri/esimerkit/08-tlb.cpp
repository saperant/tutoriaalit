// TLB on välimuisti sivutaulun alkioille. Mallinnetaan se samalla
// välimuistiluokalla: lohko = sivu. 512 x 512 -matriisi (1 MiB) luetaan
// riveittäin ja sarakkeittain.
#include <cstdint>
#include <print>

#include "yhteinen/valimuisti.hpp"

int main() {
    // @alku tlb
    constexpr std::uint32_t N = 512, alku = 0x1000'0000;
    constexpr double kavely = 30;  // jaksoa per TLB-huti (Sv32: 2 tasoa)
    std::println("{:<14} {:<15} {:>8} {:>9} {:>8}", "järjestys", "sivu",
                 "hudit", "huti-%", "jaksoa");
    for (const bool riveittain : {true, false}) {
        for (const std::uint32_t sivu : {4096u, 4u << 20}) {
            // 32-alkioinen täysin assosiatiivinen TLB.
            rv::Valimuisti tlb({.koko = 32 * sivu, .lohko = sivu,
                                .tiet = 32});
            for (std::uint32_t i = 0; i < N; ++i)
                for (std::uint32_t j = 0; j < N; ++j) {
                    const std::uint32_t r = riveittain ? i : j;
                    const std::uint32_t s = riveittain ? j : i;
                    tlb.viittaa(alku + 4 * (r * N + s), false);
                }
            const rv::VmTilastot& t = tlb.tilastot();
            const double huti = 1 - t.osumasuhde();
            std::println("{:<14} {:<15} {:>8} {:>8.3f}% {:>8.3f}",
                         riveittain ? "riveittäin" : "sarakkeittain",
                         sivu == 4096 ? "4 KiB" : "4 MiB (mega)", t.hudit,
                         100 * huti, huti * kavely);
        }
    }
    // @loppu tlb
}
