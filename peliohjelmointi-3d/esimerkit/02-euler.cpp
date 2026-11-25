// Eulerin kulmien kolme ongelmaa: kiertojen järjestys, lukkiutuminen
// nyökkäyskulmalla 90 astetta ja kulmien interpolointi.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>

// @alku asento
// Lentokoneen nokka osoittaa paikallisesti suuntaan -z ja selkä
// suuntaan +y. Kaksi vektoria kertoo asennon yksikäsitteisesti.
void tulosta(const char* nimi, Kvat q) {
    std::println("{:24} nokka {:20} selkä {}", nimi,
                 teksti(kierra(q, {0, 0, -1})), teksti(kierra(q, {0, 1, 0})));
}
// @loppu asento

int main() {
    // @alku jarjestys
    Kvat kaanto = akselikulma({0, 1, 0}, rad(90));    // vasemmalle
    Kvat nyokkays = akselikulma({1, 0, 0}, rad(90));  // nokka ylös
    std::println("Sama kaksi kiertoa eri järjestyksessä:");
    tulosta("nyökkäys, sitten kääntö", kaanto * nyokkays);
    tulosta("kääntö, sitten nyökkäys", nyokkays * kaanto);
    // @loppu jarjestys

    // @alku lukko
    std::println("\nNyökkäys 90 astetta (kääntö, kallistus):");
    tulosta("(30, 0)", eulerista(rad(30), rad(90), rad(0)));
    tulosta("(0, -30)", eulerista(rad(0), rad(90), rad(-30)));
    tulosta("(50, 20)", eulerista(rad(50), rad(90), rad(20)));
    // @loppu lukko

    // @alku kierahdys
    std::println("\nKääntö 350 astetta -> 10 astetta, puoliväli:");
    double a = 350, b = 10;
    tulosta("kulmien keskiarvo", eulerista(rad((a + b) / 2), 0, 0));
    tulosta("kvaternioiden slerp",
            slerp(eulerista(rad(a), 0, 0), eulerista(rad(b), 0, 0), 0.5));
    // @loppu kierahdys
}
