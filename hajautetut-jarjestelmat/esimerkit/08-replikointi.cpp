// Raftin lokin replikointi viassa: sata satunnaista vikaohjelmaa
// (kaatumisia ja verkon jakoja) ja turvallisuusominaisuuksien
// tarkistus jokaisessa.
#include <cstdio>

#include "yhteinen/raftkoe.hpp"

int main() {
    // @alku main
    Raftkoe ilman = aja_raft(1, {}, 4000);
    std::printf("ilman vikoja: %ld komentoa, %d termi(a)\n\n",
                ilman.valmiit, ilman.termeja);

    std::printf("esimerkki vikaohjelmasta (siemen 1):\n");
    for (const Vika& v : arvo_viat(1, 5, 8, 4000))
        std::printf("  %s\n", kuvaus(v).c_str());

    const int AJOJA = 100;
    int rikkeet = 0;
    long valmiit = 0, termeja = 0;
    for (std::uint64_t s = 1; s <= AJOJA; ++s) {
        Raftkoe k = aja_raft(s, arvo_viat(s, 5, 8, 4000), 4000);
        if (!k.rike.empty()) {
            ++rikkeet;
            std::printf("siemen %llu: %s\n",
                        static_cast<unsigned long long>(s), k.rike.c_str());
        }
        valmiit += k.valmiit;
        termeja += k.termeja;
    }
    std::printf("\n%d ajoa, 8 vikaa kussakin: %d turvallisuusriketta\n",
                AJOJA, rikkeet);
    std::printf("keskimaarin %ld komentoa ja %ld termia ajossa\n",
                valmiit / AJOJA, termeja / AJOJA);
    // @loppu main
}
