// Simulointitestin löytämän virheen pienentäminen: etsitään siemen,
// jolla virheellinen Raft rikkoo turvallisuuden, ja karsitaan sen
// vikaohjelmasta viat, joita virheen toistaminen ei tarvitse
// (delta-debuggaus, Zeller ja Hildebrandt 2002).
#define RAFT_BUGI_AANESTYS
#include <cstdio>
#include <string>
#include <vector>

#include "yhteinen/raftkoe.hpp"

// @alku ddmin
// Palauttaa pienen osajoukon, jolla `kaatuu` on yhä tosi. Jokainen
// jäljelle jäävä vika on tarpeellinen: minkä tahansa poistaminen
// kerrallaan korjaisi virheen.
template <class F>
std::vector<Vika> minimoi(std::vector<Vika> viat, F kaatuu, int& kokeita) {
    std::size_t osia = 2;
    while (viat.size() >= 2) {
        std::size_t koko = (viat.size() + osia - 1) / osia;
        bool pieneni = false;
        for (std::size_t alku = 0; alku < viat.size(); alku += koko) {
            std::vector<Vika> loput;            // poistetaan yksi osa
            for (std::size_t i = 0; i < viat.size(); ++i)
                if (i < alku || i >= alku + koko) loput.push_back(viat[i]);
            ++kokeita;
            if (kaatuu(loput)) {
                viat = std::move(loput);
                osia = std::max<std::size_t>(osia - 1, 2);
                pieneni = true;
                break;
            }
        }
        if (pieneni) continue;
        if (osia >= viat.size()) break;
        osia = std::min(osia * 2, viat.size());
    }
    return viat;
}
// @loppu ddmin

int main() {
    // @alku haku
    std::uint64_t siemen = 0;
    for (std::uint64_t s = 1; siemen == 0; ++s)
        if (!aja_raft(s, arvo_viat(s, 5, 30, 4000), 4000).rike.empty())
            siemen = s;
    std::vector<Vika> viat = arvo_viat(siemen, 5, 30, 4000);
    std::printf("siemen %llu kaatuu, vikoja %zu\n",
                static_cast<unsigned long long>(siemen), viat.size());

    int kokeita = 0;
    auto kaatuu = [siemen](const std::vector<Vika>& v) {
        return !aja_raft(siemen, v, 4000).rike.empty();
    };
    std::vector<Vika> pienin = minimoi(viat, kaatuu, kokeita);
    std::printf("pienennetty %zu vikaan %d kokeella:\n", pienin.size(),
                kokeita);
    for (const Vika& v : pienin) std::printf("  %s\n", kuvaus(v).c_str());
    // @loppu haku

    // @alku jalki
    std::printf("\njalki pienennetylla vikaohjelmalla:\n");
    Raftkoe k = aja_raft(siemen, pienin, 4000, true);
    std::printf("rike: %s\n", k.rike.c_str());
    // @loppu jalki
}
