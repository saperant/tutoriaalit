// Lyhyen merkkijonon optimointi (SSO): milloin std::string varaa muistia.
#include <cstdio>
#include <string>
#include <vector>

#include "laskuri.hpp"

int main()
{
    // @alku sso
    std::printf("sizeof(std::string) = %zu\n", sizeof(std::string));
    for (std::size_t pituus : {0, 15, 16, 22, 23, 100}) {
        laskuri::Jakso j;
        std::string s(pituus, 'k');
        std::printf("  pituus %3zu: varauksia %zu, kapasiteetti %zu\n",
                    pituus, j.varaukset(), s.capacity());
    }
    // @loppu sso

    // @alku nimet
    // Tuhat lyhyttä tunnistetta: vain vektori varaa muistia.
    laskuri::Jakso j;
    std::vector<std::string> tunnisteet;
    tunnisteet.reserve(1000);
    for (int i = 0; i < 1000; ++i) {
        tunnisteet.push_back("tuote-" + std::to_string(i));
    }
    std::printf("1000 tunnistetta: varauksia %zu\n", j.varaukset());
    // @loppu nimet
}
