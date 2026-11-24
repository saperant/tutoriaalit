// Sama koe ilman tyhjää merkintää termin alussa. Johtaja sitouttaa
// nyt edellisen termin merkintöjä usein pelkän enemmistön perusteella,
// mutta satunnainen vikaohjelma ei silti tuota tilannetta, jossa
// sitoutettu merkintä korvattaisiin.
#define RAFT_BUGI_SITOUTUS
#define RAFT_ILMAN_TYHJAA
#include <cstdio>

#include "yhteinen/raftkoe.hpp"

int main() {
    // @alku ilman
    const int AJOJA = 100;
    long suoritettu = 0;
    int ajoissa = 0, rikkeita = 0;
    for (std::uint64_t s = 1; s <= AJOJA; ++s) {
        Raftkoe k = aja_raft(s, arvo_viat(s, 5, 30, 4000), 4000);
        suoritettu += k.vanhan_termin_sitoutuksia;
        if (k.vanhan_termin_sitoutuksia > 0) ++ajoissa;
        if (!k.rike.empty()) ++rikkeita;
    }
    std::printf("%d ajoa, 30 vikaa kussakin\n", AJOJA);
    std::printf("virheellinen sitoutus suoritettiin %ld kertaa "
                "%d ajossa\n", suoritettu, ajoissa);
    std::printf("turvallisuusrikkeita: %d\n", rikkeita);
    // @loppu ilman
}
