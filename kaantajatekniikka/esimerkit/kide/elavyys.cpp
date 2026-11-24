#include "elavyys.hpp"

#include <ostream>

namespace kide {

// @alku laske
Elavyys laske_elavyys(const IrFunktio& f) {
    std::size_t n = f.nimet.size();
    std::size_t lohkoja = f.lohkot.size();
    // käyttö[b]: luetaan lohkossa ennen kirjoitusta; maar[b]: kirjoitetaan.
    std::vector<std::vector<bool>> kaytto(lohkoja, std::vector<bool>(n));
    std::vector<std::vector<bool>> maar(lohkoja, std::vector<bool>(n));
    for (std::size_t b = 0; b < lohkoja; ++b) {
        for (const Kasky& k : f.lohkot[b].kaskyt) {
            for (Vreg r : k.lahteet) {
                if (r >= 0 && !maar[b][r]) kaytto[b][r] = true;
            }
            if (k.kohde >= 0) maar[b][k.kohde] = true;
        }
    }
    Elavyys e{std::vector<std::vector<bool>>(lohkoja, std::vector<bool>(n)),
              std::vector<std::vector<bool>>(lohkoja, std::vector<bool>(n))};
    // Taaksepäin etenevä analyysi: kierretään lohkot lopusta alkuun,
    // kunnes mikään joukko ei enää muutu (kiintopiste).
    for (bool muuttui = true; muuttui;) {
        muuttui = false;
        ++e.kierroksia;
        for (std::size_t i = lohkoja; i-- > 0;) {
            std::vector<bool> ulos(n);
            for (int s : f.lohkot[i].seuraajat) {      // ulos = U sisaan[s]
                for (std::size_t r = 0; r < n; ++r) {
                    ulos[r] = ulos[r] || e.sisaan[s][r];
                }
            }
            std::vector<bool> sisaan(n);   // käyttö U (ulos - määritellyt)
            for (std::size_t r = 0; r < n; ++r) {
                sisaan[r] = kaytto[i][r] || (ulos[r] && !maar[i][r]);
            }
            if (ulos != e.ulos[i] || sisaan != e.sisaan[i]) {
                muuttui = true;
                e.ulos[i] = std::move(ulos);
                e.sisaan[i] = std::move(sisaan);
            }
        }
    }
    return e;
}
// @loppu laske

void tulosta_elavyys(const IrFunktio& f, const Elavyys& e, std::ostream& u) {
    auto joukko = [&](const std::vector<bool>& j) {
        u << '{';
        bool eka = true;
        for (std::size_t r = 0; r < j.size(); ++r) {
            if (!j[r]) continue;
            u << (eka ? "" : " ") << rekisteri(f, static_cast<Vreg>(r));
            eka = false;
        }
        u << '}';
    };
    u << "fn " << f.nimi << " (kierroksia " << e.kierroksia << ")\n";
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        u << "  L" << b << "  sisään ";
        joukko(e.sisaan[b]);
        u << "  ulos ";
        joukko(e.ulos[b]);
        u << '\n';
    }
}

}  // namespace kide
