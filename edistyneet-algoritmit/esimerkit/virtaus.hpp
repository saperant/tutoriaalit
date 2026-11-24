// virtaus.hpp: maksimivirtaus Edmondsin-Karpin ja Dinicin algoritmeilla.
#pragma once

#include <algorithm>
#include <limits>
#include <queue>
#include <vector>

// @alku verkko
// Kaaret ovat pareittain: kaari e ja sen vastakaari e ^ 1. Vastakaaren
// jäännöskapasiteetti on kaaren virta, joten virtaa voi "perua".
class Virtausverkko {
public:
    explicit Virtausverkko(int n) : vierus_(static_cast<std::size_t>(n)) {}

    int lisaa_kaari(int u, int v, long kapasiteetti)
    {
        int e = static_cast<int>(kaaret_.size());
        kaaret_.push_back({v, kapasiteetti, 0});
        kaaret_.push_back({u, 0, 0});
        vierus_[ind(u)].push_back(e);
        vierus_[ind(v)].push_back(e + 1);
        return e;
    }

    long virta(int e) const { return kaaret_[ind(e)].virta; }
    void nollaa()
    {
        for (auto& k : kaaret_) {
            k.virta = 0;
        }
    }
    // @loppu verkko

    // @alku ek
    // Edmonds-Karp: lisäyspolku leveyshaulla, eli aina lyhin polku
    // jäännösverkossa. Polkuja on O(V E), joten aika on O(V E^2).
    long edmonds_karp(int s, int t)
    {
        long yhteensa = 0;
        polkuja = 0;
        for (;;) {
            std::vector<int> tulokaari(vierus_.size(), -1);
            std::queue<int> jono;
            jono.push(s);
            while (!jono.empty() && tulokaari[ind(t)] < 0) {
                int u = jono.front();
                jono.pop();
                for (int e : vierus_[ind(u)]) {
                    int v = kaaret_[ind(e)].kohde;
                    if (v != s && tulokaari[ind(v)] < 0 && jaannos(e) > 0) {
                        tulokaari[ind(v)] = e;
                        jono.push(v);
                    }
                }
            }
            if (tulokaari[ind(t)] < 0) {
                return yhteensa;   // t ei saavutettavissa: virta on suurin
            }
            // Polku kuljetaan takaperin: vastakaari osoittaa edelliseen.
            auto edellinen = [&](int v) {
                return kaaret_[ind(tulokaari[ind(v)] ^ 1)].kohde;
            };
            long lisa = std::numeric_limits<long>::max();
            for (int v = t; v != s; v = edellinen(v)) {
                lisa = std::min(lisa, jaannos(tulokaari[ind(v)]));
            }
            for (int v = t; v != s; v = edellinen(v)) {
                kaaret_[ind(tulokaari[ind(v)])].virta += lisa;
                kaaret_[ind(tulokaari[ind(v)] ^ 1)].virta -= lisa;
            }
            yhteensa += lisa;
            ++polkuja;
        }
    }
    // @loppu ek

    // @alku dinic
    // Dinic: leveyshaku jakaa solmut tasoihin etäisyyden mukaan, ja
    // syvyyshaku lähettää virtaa vain tasolta seuraavalle, kunnes yhtään
    // polkua ei ole (estävä virta). Vaiheita on enintään V, ja aika on
    // O(V^2 E); kaksijakoisessa parituksessa O(E sqrt V).
    long dinic(int s, int t)
    {
        long yhteensa = 0;
        vaiheita = 0;
        while (tasoita(s, t)) {
            ++vaiheita;
            seuraava_.assign(vierus_.size(), 0);
            constexpr long rajaton = std::numeric_limits<long>::max();
            while (long lisa = laheta(s, t, rajaton)) {
                yhteensa += lisa;
            }
        }
        return yhteensa;
    }
    // @loppu dinic

    // @alku leikkaus
    // Minimileikkaus suurimman virran jälkeen: s:stä jäännösverkossa
    // saavutettavat solmut. Niistä ulos johtavat kaaret ovat täynnä.
    std::vector<bool> s_puoli(int s) const
    {
        std::vector<bool> nahty(vierus_.size(), false);
        std::vector<int> pino{s};
        nahty[ind(s)] = true;
        while (!pino.empty()) {
            int u = pino.back();
            pino.pop_back();
            for (int e : vierus_[ind(u)]) {
                int v = kaaret_[ind(e)].kohde;
                if (!nahty[ind(v)] && jaannos(e) > 0) {
                    nahty[ind(v)] = true;
                    pino.push_back(v);
                }
            }
        }
        return nahty;
    }
    // @loppu leikkaus

    int polkuja = 0, vaiheita = 0;

private:
    struct Kaari {
        int kohde;
        long kapasiteetti, virta;
    };

    static std::size_t ind(int i) { return static_cast<std::size_t>(i); }
    long jaannos(int e) const
    {
        return kaaret_[ind(e)].kapasiteetti - kaaret_[ind(e)].virta;
    }

    bool tasoita(int s, int t)
    {
        taso_.assign(vierus_.size(), -1);
        taso_[ind(s)] = 0;
        std::queue<int> jono;
        jono.push(s);
        while (!jono.empty()) {
            int u = jono.front();
            jono.pop();
            for (int e : vierus_[ind(u)]) {
                int v = kaaret_[ind(e)].kohde;
                if (taso_[ind(v)] < 0 && jaannos(e) > 0) {
                    taso_[ind(v)] = taso_[ind(u)] + 1;
                    jono.push(v);
                }
            }
        }
        return taso_[ind(t)] >= 0;
    }

    // seuraava_[u] muistaa, mihin asti u:n kaaret on käyty: umpikujaan
    // johtanutta kaarta ei kokeilla samassa vaiheessa uudelleen.
    long laheta(int u, int t, long raja)
    {
        if (u == t) {
            return raja;
        }
        auto& i = seuraava_[ind(u)];
        for (; i < vierus_[ind(u)].size(); ++i) {
            int e = vierus_[ind(u)][i];
            int v = kaaret_[ind(e)].kohde;
            if (taso_[ind(v)] == taso_[ind(u)] + 1 && jaannos(e) > 0) {
                if (long d = laheta(v, t, std::min(raja, jaannos(e)))) {
                    kaaret_[ind(e)].virta += d;
                    kaaret_[ind(e ^ 1)].virta -= d;
                    return d;
                }
            }
        }
        return 0;
    }

    std::vector<std::vector<int>> vierus_;
    std::vector<Kaari> kaaret_;
    std::vector<int> taso_;
    std::vector<std::size_t> seuraava_;
};
