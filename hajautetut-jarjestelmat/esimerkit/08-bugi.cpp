// Sama simulointitesti Raftille, jonka äänestyksestä puuttuu lokin
// tuoreuden tarkistus. Testi etsii siemenen, jolla turvallisuus
// rikkoutuu, ja tulostaa vikaohjelman.
#define RAFT_BUGI_AANESTYS
#include <cstdio>

#include "yhteinen/raftkoe.hpp"

int main() {
    // @alku haku
    int loydetyt = 0;
    std::uint64_t ensimmainen = 0;
    for (std::uint64_t s = 1; s <= 100; ++s) {
        Raftkoe k = aja_raft(s, arvo_viat(s, 5, 8, 4000), 4000);
        if (k.rike.empty()) continue;
        if (++loydetyt == 1) {
            ensimmainen = s;
            std::printf("siemen %llu: %s\n",
                        static_cast<unsigned long long>(s), k.rike.c_str());
        }
    }
    std::printf("rike %d ajossa sadasta\n", loydetyt);
    std::printf("\nsiemenen %llu vikaohjelma:\n",
                static_cast<unsigned long long>(ensimmainen));
    for (const Vika& v : arvo_viat(ensimmainen, 5, 8, 4000))
        std::printf("  %s\n", kuvaus(v).c_str());
    // @loppu haku
}
