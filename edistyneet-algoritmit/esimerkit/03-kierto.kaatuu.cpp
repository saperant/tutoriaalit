// Virheellinen kierto: kierra_vasen() ei anna nousevalle solmulle
// vanhan juuren väriä. Haut toimivat yhä, mutta tasapaino on rikki.
#define KIERTOVIRHE
#include <print>
#include <set>

#include "punamusta.hpp"
#include "testaus.hpp"

int main()
{
    Satunnainen s{1};
    PunamustaPuu puu;
    std::set<int> malli;
    for (int i = 0; i < 1000; ++i) {
        int x = s.valilta(0, 9999);
        puu.lisaa(x);
        malli.insert(x);
        vaadi(puu.sisaltaa(x), "lisätty avain puuttuu");
    }
    vaadi(puu.alkiot() == std::vector(malli.begin(), malli.end()),
          "sisältö poikkeaa mallista");
    std::println("1000 lisäystä: sisältö täsmää malliin");
    if (auto rike = puu.tarkista()) {
        vaadi(false, "invariantti rikki: " + *rike);
    }
}
