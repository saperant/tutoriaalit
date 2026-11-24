// string_view ja span parametreina: ei väliaikaisia kopioita.
#include <algorithm>
#include <array>
#include <cstdio>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include "laskuri.hpp"

// @alku merkkijono
const std::array<std::string_view, 3> varatut{
    "administrator", "system-account", "maintenance-user"};

// Kutsu merkkijonoliteraalilla rakentaa väliaikaisen std::stringin.
bool on_varattu(const std::string& nimi)
{
    return std::ranges::find(varatut, nimi) != varatut.end();
}

// Näkymä ei omista merkkejä eikä varaa muistia.
bool on_varattu_nakyma(std::string_view nimi)
{
    return std::ranges::find(varatut, nimi) != varatut.end();
}
// @loppu merkkijono

// @alku span
// Vektoriviittaus pakottaa kutsujan rakentamaan vektorin.
int summa(const std::vector<int>& x)
{
    int s = 0;
    for (int v : x) {
        s += v;
    }
    return s;
}

// span kelpaa mille tahansa yhtenäiselle taulukolle.
int summa_span(std::span<const int> x)
{
    int s = 0;
    for (int v : x) {
        s += v;
    }
    return s;
}
// @loppu span

int main()
{
    // @alku kaytto
    {
        laskuri::Jakso j;
        bool b = on_varattu("maintenance-user");
        std::printf("const std::string&: %d, varauksia %zu\n", b,
                    j.varaukset());
    }
    {
        laskuri::Jakso j;
        bool b = on_varattu_nakyma("maintenance-user");
        std::printf("std::string_view:   %d, varauksia %zu\n", b,
                    j.varaukset());
    }
    std::array<int, 64> mittaukset{};
    mittaukset.fill(2);
    {
        laskuri::Jakso j;
        int s = summa({mittaukset.begin(), mittaukset.end()});
        std::printf("const vector&:      %d, varauksia %zu\n", s,
                    j.varaukset());
    }
    {
        laskuri::Jakso j;
        int s = summa_span(mittaukset);
        std::printf("std::span:          %d, varauksia %zu\n", s,
                    j.varaukset());
    }
    // @loppu kaytto
}
