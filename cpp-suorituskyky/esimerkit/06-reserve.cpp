// Vektorin ja merkkijonon kasvu: varaukset ilman reservea ja sen kanssa.
#include <cstdio>
#include <string>
#include <vector>

#include "laskuri.hpp"

int main()
{
    // @alku kapasiteetti
    std::vector<int> v;
    std::printf("kapasiteetit:");
    auto edellinen = v.capacity();
    for (int i = 0; i < 1000; ++i) {
        v.push_back(i);
        if (v.capacity() != edellinen) {
            edellinen = v.capacity();
            std::printf(" %zu", edellinen);
        }
    }
    std::printf("\n");
    // @loppu kapasiteetti

    // @alku reserve
    {
        laskuri::Jakso j;
        std::vector<int> ilman;
        for (int i = 0; i < 1000; ++i) {
            ilman.push_back(i);
        }
        std::printf("ilman reservea: varauksia %zu, tavuja %zu\n",
                    j.varaukset(), j.tavut());
    }
    {
        laskuri::Jakso j;
        std::vector<int> varattu;
        varattu.reserve(1000);
        for (int i = 0; i < 1000; ++i) {
            varattu.push_back(i);
        }
        std::printf("reserve(1000):  varauksia %zu, tavuja %zu\n",
                    j.varaukset(), j.tavut());
    }
    // @loppu reserve

    // @alku merkkijono
    std::string osa(40, 'x');
    {
        laskuri::Jakso j;
        std::string s = osa + "," + osa + "," + osa;
        std::printf("a + b + c:      varauksia %zu\n", j.varaukset());
    }
    {
        laskuri::Jakso j;
        std::string s;
        s.reserve(3 * osa.size() + 2);
        s.append(osa).append(",").append(osa).append(",").append(osa);
        std::printf("reserve+append: varauksia %zu\n", j.varaukset());
    }
    // @loppu merkkijono
}
