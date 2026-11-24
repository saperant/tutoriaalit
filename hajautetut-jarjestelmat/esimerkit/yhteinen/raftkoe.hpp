// Raft-klusterin simulointitesti: viisi palvelinta, kaksi asiakasta,
// häviävä verkko ja satunnainen vikaohjelma. Turvallisuus tarkistetaan
// tapahtumien aikana ja lokit 10 ms välein.
#pragma once
#include <memory>
#include <string>
#include <vector>

#include "raft.hpp"
#include "viat.hpp"

// @alku koe
constexpr int N = 5, ASIAKKAITA = 2;

struct Raftkoe {
    std::string rike;        // ensimmäinen turvallisuusrike tai tyhjä
    long valmiit = 0;        // asiakkaiden vahvistetut komennot
    long sovelluksia = 0;
    long vanhan_termin_sitoutuksia = 0;
    int termeja = 0;
};

inline Raftkoe aja_raft(std::uint64_t siemen, const std::vector<Vika>& viat,
                        Aika kesto, bool loki = false) {
    Tarkkailija tark;
    Verkkoasetukset a{.viive_min = 1, .viive_max = 20, .katoaa = 20,
                      .monistuu = 20};
    Simulaattori<RaftViesti, RaftLevy> sim(N + ASIAKKAITA, siemen, a,
        [&tark](int i, RaftLevy& levy)
            -> std::unique_ptr<Solmu<RaftViesti>> {
            if (i >= N) return std::make_unique<RaftAsiakas>(N);
            return std::make_unique<RaftSolmu>(N, levy, tark);
        });
    sim.tulosta_loki(loki);
    asenna(sim, viat);
    for (Aika t = 10; t <= kesto + 1000; t += 10)
        sim.kun(t, [&] { tarkista_lokit(sim, N, tark); });
    sim.aja(kesto + 1000);
    Raftkoe k{.rike = tark.ensimmainen, .valmiit = 0,
              .sovelluksia = tark.sovelluksia,
              .vanhan_termin_sitoutuksia = tark.vanhan_termin_sitoutuksia,
              .termeja = tark.termeja()};
    for (int i = N; i < N + ASIAKKAITA; ++i)
        k.valmiit += sim.solmu<RaftAsiakas>(i)->valmiit;
    return k;
}
// @loppu koe
