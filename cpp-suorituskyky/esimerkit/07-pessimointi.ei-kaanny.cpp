// std::move paluulausekkeessa estää kopion poiston. GCC ja Clang
// varoittavat (-Wpessimizing-move), ja -Werror tekee varoituksesta virheen.
#include <utility>

#include "seuranta.hpp"

// @alku pessimointi
Seurattava kokoa()
{
    Seurattava tulos{"koottu"};
#ifndef KORJATTU
    return std::move(tulos);     // siirto: NRVO ei ole enää mahdollinen
#else
    return tulos;                // NRVO tai implisiittinen siirto
#endif
}
// @loppu pessimointi

int main()
{
    auto t = kokoa();
    Seurattava::raportoi("kokoa()");
    std::printf("%s\n", t.arvo.c_str());
}
