// Rekisterien uudelleennimeäminen: summaussilmukan kaksi kierrosta
// nimetään uudelleen, ja riippuvuudet lasketaan ennen ja jälkeen.
#include <algorithm>
#include <array>
#include <print>
#include <string>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/ohjelmat.hpp"

// @alku nimeaminen
// Käsky nimettynä: mitä rekistereitä se lukee ja minkä se kirjoittaa.
// -1 tarkoittaa, ettei käsky lue tai kirjoita rekisteriä.
struct Nimetty { int lukee1 = -1, lukee2 = -1, kirjoittaa = -1; };

// Nimeämistaulu (RAT) kertoo, missä fyysisessä rekisterissä kunkin
// arkkitehtuurisen rekisterin tuorein arvo on. Jokainen kirjoitus saa
// vapaiden listalta uuden fyysisen rekisterin.
std::vector<Nimetty> nimea(const std::vector<rv::Tapahtuma>& jalki,
                           std::array<int, 32>& rat, int& vapaa) {
    std::vector<Nimetty> tulos;
    for (const rv::Tapahtuma& k : jalki) {
        Nimetty n;
        // Lähteet luetaan taulusta ennen kuin kohde päivittää sen.
        if (k.lukee_rs1) n.lukee1 = rat[k.f.rs1];
        if (k.lukee_rs2) n.lukee2 = rat[k.f.rs2];
        if (k.kirjoittaa_rd) n.kirjoittaa = rat[k.f.rd] = vapaa++;
        tulos.push_back(n);
    }
    return tulos;
}
// @loppu nimeaminen

// @alku riippuvuudet
struct Riippuvuudet { int raw = 0, war = 0, waw = 0; };

// RAW: käsky lukee arvon, jonka aiempi ikkunan käsky kirjoittaa.
// WAW: käsky kirjoittaa samaan nimeen kuin aiempi kirjoittaja.
// WAR: käsky kirjoittaa nimeen, jonka aiempi käsky vielä lukee.
Riippuvuudet laske(const std::vector<Nimetty>& k) {
    Riippuvuudet r;
    for (std::size_t j = 0; j < k.size(); ++j) {
        for (const int lahde : {k[j].lukee1, k[j].lukee2}) {
            if (lahde < 0) continue;
            for (std::size_t i = j; i-- > 0;)
                if (k[i].kirjoittaa == lahde) { ++r.raw; break; }
        }
        if (k[j].kirjoittaa < 0) continue;
        for (std::size_t i = j; i-- > 0;) {
            if (k[i].lukee1 == k[j].kirjoittaa ||
                k[i].lukee2 == k[j].kirjoittaa) ++r.war;
            if (k[i].kirjoittaa == k[j].kirjoittaa) { ++r.waw; break; }
        }
    }
    return r;
}
// @loppu riippuvuudet

std::string taulu(const std::array<int, 32>& rat) {
    std::string s;
    for (const rv::u32 x : {5u, 6u, 7u, 8u, 9u, 10u})   // t0 t1 t2 s0 s1 a0
        s += std::format(" {}=p{}", rv::abi_nimet[x], rat[x]);
    return s;
}

int main() {
    // @alku ajo
    const rv::Ohjelma o = rv::koota(ohjelmat::summa);
    rv::Kone kone(o);
    const std::vector<rv::Tapahtuma> koko = kone.aja();
    const auto it = std::ranges::find(koko, o.nimiot.at("summaa"),
                                      &rv::Tapahtuma::pc);
    const std::vector<rv::Tapahtuma> ikkuna(it, it + 12);  // kaksi kierrosta

    std::array<int, 32> rat;
    for (int x = 0; x < 32; ++x) rat[static_cast<std::size_t>(x)] = x;
    int vapaa = 32;                        // p0–p31 ovat alkutilan arvot
    std::println("nimeämistaulu ennen:  {}", taulu(rat));
    const std::vector<Nimetty> fyys = nimea(ikkuna, rat, vapaa);
    std::println("{:<22}{:<10}{}", "käsky", "lukee", "kirjoittaa");
    std::vector<Nimetty> arkk;
    for (std::size_t i = 0; i < ikkuna.size(); ++i) {
        const rv::Tapahtuma& k = ikkuna[i];
        arkk.push_back({k.lukee_rs1 ? static_cast<int>(k.f.rs1) : -1,
                        k.lukee_rs2 ? static_cast<int>(k.f.rs2) : -1,
                        k.kirjoittaa_rd ? static_cast<int>(k.f.rd) : -1});
        std::string lukee;
        for (const int p : {fyys[i].lukee1, fyys[i].lukee2})
            if (p >= 0) lukee += std::format("p{} ", p);
        std::println("{:<22}{:<10}{}", rv::pura_teksti(k.kasky, k.pc), lukee,
                     fyys[i].kirjoittaa < 0
                         ? std::string("-")
                         : std::format("{} -> p{}", rv::abi_nimet[k.f.rd],
                                       fyys[i].kirjoittaa));
    }
    std::println("nimeämistaulu jälkeen:{}", taulu(rat));
    const Riippuvuudet a = laske(arkk), f = laske(fyys);
    std::println("\n{:<26}{:>4}{:>5}{:>5}", "riippuvuudet", "RAW", "WAR",
                 "WAW");
    std::println("{:<26}{:>4}{:>5}{:>5}", "arkkitehtuuriset nimet", a.raw,
                 a.war, a.waw);
    std::println("{:<26}{:>4}{:>5}{:>5}", "fyysiset nimet", f.raw, f.war,
                 f.waw);
    // @loppu ajo
}
