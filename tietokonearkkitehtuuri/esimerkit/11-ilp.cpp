// Käskytason rinnakkaisuus: kuinka monta käskyä jaksossa (IPC) eri
// levyiset järjestyksessä ja epäjärjestyksessä suorittavat ytimet
// saavat samoista käskyjäljistä. Rajatutkimus: muisti osuu aina.
#include <algorithm>
#include <array>
#include <print>
#include <string_view>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/liukuhihna.hpp"
#include "yhteinen/ohjelmat.hpp"

// @alku malli
struct Ydin {
    int leveys;          // käskyä jaksossa (nouto, liikkeelle, valmis)
    int ikkuna;          // 0 = järjestyksessä, muuten uudelleenjärj.puskuri
    bool uudelleennimeys = true;
    bool ennustin = false;  // false = täydellinen ennustus
};

int viive(const rv::Tapahtuma& t) {
    if (t.lataus) return 2;
    if (t.f.opcode == 0x33 && t.f.funct7 == 1) return 3;  // mul
    return 1;
}

double ipc(const std::vector<rv::Tapahtuma>& jalki, const Ydin& y) {
    const std::size_t n = jalki.size();
    std::vector<long> liikkeelle(n), valmis(n), poistuu(n);
    std::vector<int> paikat;                  // liikkeelle lähteneet/jakso
    std::array<long, 32> arvo{}, luettu{}, kirjoitettu{};
    rv::Laskuri e(2, 64);
    long nouto = 0, noudettu = 0;             // noutojakso ja sen käskyt
    for (std::size_t i = 0; i < n; ++i) {
        const rv::Tapahtuma& k = jalki[i];
        if (noudettu == y.leveys) { ++nouto; noudettu = 0; }
        // Ikkuna täynnä: odotetaan, että vanhin käsky poistuu.
        if (y.ikkuna > 0 && i >= static_cast<std::size_t>(y.ikkuna))
            nouto = std::max(nouto, poistuu[i - y.ikkuna]);
        ++noudettu;
        long t = nouto + 1;                   // aikaisin liikkeellelähtö
        if (y.ikkuna == 0 && i > 0) t = std::max(t, liikkeelle[i - 1]);
        if (k.lukee_rs1) t = std::max(t, arvo[k.f.rs1]);
        if (k.lukee_rs2) t = std::max(t, arvo[k.f.rs2]);
        if (!y.uudelleennimeys && k.kirjoittaa_rd)  // WAR ja WAW
            t = std::max({t, luettu[k.f.rd], kirjoitettu[k.f.rd]});
        while (static_cast<long>(paikat.size()) <= t) paikat.push_back(0);
        while (paikat[t] == y.leveys) {       // jakson paikat käytetty
            ++t;
            if (static_cast<long>(paikat.size()) <= t) paikat.push_back(0);
        }
        ++paikat[t];
        liikkeelle[i] = t;
        valmis[i] = t + viive(k);
        if (k.lukee_rs1) luettu[k.f.rs1] = std::max(luettu[k.f.rs1], t);
        if (k.lukee_rs2) luettu[k.f.rs2] = std::max(luettu[k.f.rs2], t);
        if (k.kirjoittaa_rd) {
            arvo[k.f.rd] = valmis[i];
            kirjoitettu[k.f.rd] = valmis[i];
        }
        poistuu[i] = std::max(valmis[i], i ? poistuu[i - 1] : 0);
        // Väärin ennustettu haara: nouto jatkuu vasta haaran ratkettua.
        if (y.ennustin && k.haara) {
            const bool arvaus = e.ennusta(k.pc, 0);
            e.paivita(k.pc, k.otettu);
            if (arvaus != k.otettu) {
                nouto = std::max(nouto, valmis[i]) + 1;
                noudettu = 0;
            }
        }
    }
    return static_cast<double>(n) / static_cast<double>(poistuu[n - 1]);
}
// @loppu malli

int main() {
    // @alku vertailu
    const std::array<std::pair<std::string_view, std::string_view>, 5>
        testit{{{"summa", ohjelmat::summa}, {"kupla", ohjelmat::kupla},
                {"matriisi", ohjelmat::matriisi}, {"fib", ohjelmat::fib},
                {"lista", ohjelmat::lista}}};
    std::vector<std::vector<rv::Tapahtuma>> jaljet;
    for (const auto& t : testit) {
        rv::Kone kone(rv::koota(t.second));
        jaljet.push_back(kone.aja());
    }
    const std::array<std::pair<std::string_view, Ydin>, 8> ytimet{{
        {"1-leveä, järj.", {1, 0}},
        {"2-leveä, järj.", {2, 0}},
        {"4-leveä, järj.", {4, 0}},
        {"4-leveä, ikk. 16", {4, 16}},
        {"4-leveä, ikk. 128", {4, 128}},
        {"  ei uudelleennim.", {4, 128, false}},
        {"  2-bit. ennustin", {4, 128, true, true}},
        {"8-leveä, ikk. 512", {8, 512}}}};
    std::print("{:<19}", "IPC");
    for (const auto& t : testit) std::print("{:>9}", t.first);
    std::println();
    for (const auto& [nimi, y] : ytimet) {
        std::print("{:<19}", nimi);
        for (const auto& jalki : jaljet)
            std::print("{:>9.2f}", ipc(jalki, y));
        std::println();
    }
    // @loppu vertailu
}
