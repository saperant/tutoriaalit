// Liukuhihnakaavio summa-ohjelman summaussilmukasta ilman
// eteenpäinkytkentää ja sen kanssa. ** tarkoittaa pysähdystä.
#include <algorithm>
#include <print>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/liukuhihna.hpp"
#include "yhteinen/ohjelmat.hpp"

int main() {
    // @alku kaavio
    const rv::Ohjelma o = rv::koota(ohjelmat::summa);
    rv::Kone kone(o);
    const std::vector<rv::Tapahtuma> koko = kone.aja();
    // Otetaan jäljestä summaa-silmukan ensimmäinen kierros ja vähän päälle.
    const rv::u32 alku = o.nimiot.at("summaa");
    const auto it = std::ranges::find(koko, alku, &rv::Tapahtuma::pc);
    const std::vector<rv::Tapahtuma> pala(it, it + 7);
    for (const bool ek : {false, true}) {
        std::vector<rv::Vaiheet> v;
        const rv::Tulos t = rv::simuloi(pala, {.eteenpainkytkenta = ek}, &v);
        std::println("eteenpäinkytkentä {}: {} jaksoa, {} pysähdystä",
                     ek ? "päällä" : "pois", t.syklit, t.datapysahdykset);
        // Ilman kytkentää kaavio on niin leveä, että viimeinen rivi
        // jätetään pois.
        std::print("{}", rv::piirra(pala, v, ek ? 7 : 6));
    }
    // @loppu kaavio
}
