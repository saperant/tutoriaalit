// Lamportin kello ja vektorikello samoille tapahtumille: Lamportin
// leima on yhteensopiva syy-seuraussuhteen kanssa, mutta vain
// vektorikello tunnistaa samanaikaiset tapahtumat. Lopuksi
// vektorikelloilla versioitu avain, jonka samanaikaiset kirjoitukset
// säilyvät sisaruksina.
#include <cstdio>
#include <string>
#include <vector>

#include "yhteinen/kellot.hpp"

const char* nimi(Suhde s) {
    switch (s) {
    case Suhde::Sama: return "sama";
    case Suhde::Ennen: return "ennen";
    case Suhde::Jalkeen: return "jalkeen";
    case Suhde::Samanaikainen: return "samanaikainen";
    }
    return "?";
}

// @alku prosessit
struct Prosessi {
    Lamport lamport;
    Vektorikello vektori{3};
};

struct Leimat {
    std::int64_t lamport;
    Vektorikello vektori;
};

struct Viesti {
    std::int64_t lamport;
    Vektorikello vektori;
};

Leimat paikallinen(Prosessi& p, std::size_t i) {
    p.vektori.tapahtuma(i);
    return {p.lamport.tapahtuma(), p.vektori};
}
Leimat laheta(Prosessi& p, std::size_t i, Viesti& ulos) {
    p.vektori.tapahtuma(i);
    ulos = {p.lamport.lahetys(), p.vektori};
    return {ulos.lamport, p.vektori};
}
Leimat vastaanota(Prosessi& p, std::size_t i, const Viesti& m) {
    p.vektori.yhdista(m.vektori);
    p.vektori.tapahtuma(i);
    return {p.lamport.vastaanotto(m.lamport), p.vektori};
}
// @loppu prosessit

// @alku sisarukset
// Ostoskori, jonka jokainen versio kantaa vektorikelloa. Uusi versio
// korvaa ne, jotka se kattaa; samanaikaiset versiot jäävät rinnakkain.
struct Versio {
    std::string arvo;
    Vektorikello kello;
};

void tallenna(std::vector<Versio>& versiot, Versio uusi) {
    std::vector<Versio> jaljelle;
    for (auto& v : versiot) {
        Suhde s = v.kello.vertaa(uusi.kello);
        if (s == Suhde::Jalkeen || s == Suhde::Sama) return;  // vanha
        if (s == Suhde::Samanaikainen) jaljelle.push_back(v);
    }
    jaljelle.push_back(std::move(uusi));
    versiot = std::move(jaljelle);
}

void tulosta(const char* otsikko, const std::vector<Versio>& versiot) {
    std::printf("%-28s", otsikko);
    for (const auto& v : versiot)
        std::printf(" {%s %s}", v.arvo.c_str(), v.kello.teksti().c_str());
    std::printf("\n");
}
// @loppu sisarukset

int main() {
    // @alku tapahtumat
    Prosessi p[3];
    Viesti m1{0, Vektorikello(3)}, m2{0, Vektorikello(3)};
    std::vector<std::pair<std::string, Leimat>> t;
    t.push_back({"a P0 paikallinen", paikallinen(p[0], 0)});
    t.push_back({"b P0 lahettaa m1", laheta(p[0], 0, m1)});
    t.push_back({"c P1 paikallinen", paikallinen(p[1], 1)});
    t.push_back({"d P1 vastaanottaa m1", vastaanota(p[1], 1, m1)});
    t.push_back({"e P1 lahettaa m2", laheta(p[1], 1, m2)});
    t.push_back({"f P2 paikallinen", paikallinen(p[2], 2)});
    t.push_back({"g P2 vastaanottaa m2", vastaanota(p[2], 2, m2)});
    // @loppu tapahtumat

    std::printf("tapahtuma              lamport  vektori\n");
    for (auto& [n, l] : t)
        std::printf("%-22s %7lld  %s\n", n.c_str(),
                    static_cast<long long>(l.lamport),
                    l.vektori.teksti().c_str());

    std::printf("\npari  lamport-leimat  vektorikello\n");
    for (auto [i, j] : {std::pair{0, 6}, {2, 5}, {5, 3}, {2, 3}}) {
        const auto& a = t[static_cast<size_t>(i)].second;
        const auto& b = t[static_cast<size_t>(j)].second;
        std::printf("%c-%c   %5lld %5lld     %s\n", 'a' + i, 'a' + j,
                    static_cast<long long>(a.lamport),
                    static_cast<long long>(b.lamport),
                    nimi(a.vektori.vertaa(b.vektori)));
    }

    // @alku kori
    std::printf("\n");
    std::vector<Versio> kori;
    Vektorikello k(3);
    k.tapahtuma(0);                               // replika 0 kirjoittaa
    tallenna(kori, {"maito", k});
    tulosta("r0 kirjoittaa maito:", kori);
    Vektorikello k1 = k;                          // r1 on nähnyt version
    k1.tapahtuma(1);
    tallenna(kori, {"maito,leipa", k1});
    tulosta("r1 lisaa leipa:", kori);
    Vektorikello k2 = k;                          // r2 ei ole nähnyt r1:tä
    k2.tapahtuma(2);
    tallenna(kori, {"maito,kahvi", k2});
    tulosta("r2 lisaa kahvi:", kori);
    Vektorikello yhd = k1;                        // asiakas yhdistää
    yhd.yhdista(k2);
    yhd.tapahtuma(0);
    tallenna(kori, {"maito,leipa,kahvi", yhd});
    tulosta("asiakas yhdistaa:", kori);
    // @loppu kori
}
