// Punamustan puun vertailutesti ja korkeus järjestetyllä syötteellä.
#include <cmath>
#include <print>
#include <set>

#include "punamusta.hpp"
#include "testaus.hpp"

int main()
{
    // @alku testi
    // Jokaisen operaation jälkeen tarkistetaan invariantit ja tulos
    // mallia vastaan; lopuksi koko sisältö.
    int operaatioita = 0;
    for (std::uint64_t siemen = 1; siemen <= 30; ++siemen) {
        Satunnainen s{siemen};
        PunamustaPuu puu;
        std::set<int> malli;
        for (int i = 0; i < 1500; ++i, ++operaatioita) {
            int x = s.valilta(0, 199);
            if (s.alle(3) == 0) {
                puu.poista(x);
                malli.erase(x);
            } else {
                puu.lisaa(x);
                malli.insert(x);
            }
            vaadi(puu.sisaltaa(x) == malli.contains(x), "haku poikkeaa");
            if (auto rike = puu.tarkista()) {
                vaadi(false, "invariantti rikki: " + *rike);
            }
        }
        vaadi(puu.alkiot() == std::vector(malli.begin(), malli.end()),
              "sisältö poikkeaa mallista");
    }
    std::println("vertailutesti: {} operaatiota, invariantit kunnossa",
                 operaatioita);
    // @loppu testi

    // @alku korkeus
    for (int n : {1000, 100000}) {
        PunamustaPuu puu;
        for (int x = 0; x < n; ++x) {
            puu.lisaa(x);   // pahin syöte tavalliselle hakupuulle
        }
        std::println("n = {:6}: korkeus {:2}, log2 n = {:4.1f}, "
                     "raja 2 log2 n = {:4.1f}", n, puu.korkeus(),
                     std::log2(n), 2 * std::log2(n));
    }
    // @loppu korkeus
}
