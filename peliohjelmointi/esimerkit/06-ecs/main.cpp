// Sama pelimaailma ECS:llä: kyvyt ovat komponentteja, ja järjestelmät
// käsittelevät kaikki entiteetit, joilla on tarvittavat komponentit.
#include "rekisteri.hpp"

#include <print>
#include <string>

// @alku komponentit
struct Paikka { double x = 0.0, y = 0.0; };
struct Nopeus { double vx = 0.0; };
struct Lentaa {};                       // merkkikomponentti
struct Ampuu { double latausaika = 0.0; int ammuttu = 0; };
struct Nimi { std::string teksti; };
// @loppu komponentit

int main() {
    Rekisteri r;
    // @alku kokoaminen
    auto lepakko = r.luo();
    r.lisaa(lepakko, Paikka{});
    r.lisaa(lepakko, Nopeus{1.0});
    r.lisaa(lepakko, Lentaa{});
    r.lisaa(lepakko, Nimi{"lepakko"});

    auto tykki = r.luo();
    r.lisaa(tykki, Paikka{});
    r.lisaa(tykki, Ampuu{});
    r.lisaa(tykki, Nimi{"tykkimies"});

    auto lentava_ampuja = r.luo();  // uusi yhdistelmä ilman uutta luokkaa
    r.lisaa(lentava_ampuja, Paikka{});
    r.lisaa(lentava_ampuja, Nopeus{2.0});
    r.lisaa(lentava_ampuja, Lentaa{});
    r.lisaa(lentava_ampuja, Ampuu{});
    r.lisaa(lentava_ampuja, Nimi{"lentävä ampuja"});
    // @loppu kokoaminen

    constexpr double dt = 1.0 / 60.0;
    for (int i = 0; i < 180; ++i) {
        // @alku jarjestelmat
        r.kaikille<Nopeus, Paikka>(
            [&](Nopeus& n, Paikka& p) { p.x += n.vx * dt; });
        r.kaikille<Lentaa, Paikka>([](Lentaa&, Paikka& p) { p.y = 2.0; });
        r.kaikille<Ampuu>([&](Ampuu& a) {
            a.latausaika -= dt;
            if (a.latausaika <= 0.0) {
                ++a.ammuttu;
                a.latausaika = 1.0;
            }
        });
        // @loppu jarjestelmat
    }
    r.kaikille<Nimi, Paikka>([](Nimi& n, Paikka& p) {
        std::println("{:15} x = {:.1f}, y = {:.1f}", n.teksti, p.x, p.y);
    });
    r.kaikille<Nimi, Ampuu>([](Nimi& n, Ampuu& a) {
        std::println("{:15} ampui {} kertaa", n.teksti, a.ammuttu);
    });

    // @alku sukupolvi
    r.tuhoa(lepakko);
    auto uusi = r.luo();  // kierrättää lepakon indeksin
    std::println("uusi indeksi {} (sukupolvi {}), lepakko elossa: {}",
                 uusi.indeksi, uusi.sukupolvi, r.elossa(lepakko));
    std::println("vanhalla tunnisteella paikka: {}",
                 r.hae<Paikka>(lepakko) ? "löytyy" : "ei löydy");
    // @loppu sukupolvi
}
