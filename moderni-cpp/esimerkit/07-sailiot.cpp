#include <array>
#include <map>
#include <print>
#include <span>
#include <string>
#include <unordered_map>
#include <vector>

// @alku span
double keskiarvo(std::span<const double> arvot)
{
    double summa = 0;
    for (double x : arvot) {
        summa += x;
    }
    return arvot.empty() ? 0.0 : summa / arvot.size();
}
// @loppu span

int main()
{
    // @alku span-kaytto
    std::vector<double> mittaukset{2.0, 4.0, 9.0};
    std::array<double, 4> kiintea{1.0, 2.0, 3.0, 4.0};
    double c_taulukko[] = {10.0, 20.0};

    std::println("{} {} {}", keskiarvo(mittaukset), keskiarvo(kiintea),
                 keskiarvo(c_taulukko));
    std::println("{}", keskiarvo(std::span{kiintea}.first(2)));
    // @loppu span-kaytto

    // @alku sanat
    std::vector<std::string> sanat{"omena", "kiivi", "omena",
                                   "luumu", "kiivi", "omena"};
    std::unordered_map<std::string, int> laskurit;
    for (const auto& sana : sanat) {
        ++laskurit[sana];   // puuttuva avain alustetaan nollaksi
    }

    // Järjestetään tulostusta varten.
    std::map<std::string, int> jarjestetty(laskurit.begin(),
                                           laskurit.end());
    for (const auto& [s, n] : jarjestetty) {
        std::println("{}: {}", s, n);
    }
    // @loppu sanat

    // @alku haku
    std::println("sisältää luumun: {}", jarjestetty.contains("luumu"));
    auto [it, lisatty] = jarjestetty.try_emplace("päärynä", 1);
    std::println("{} lisätty: {}", it->first, lisatty);
    std::erase_if(jarjestetty, [](const auto& pari) {
        return pari.second < 2;
    });
    std::println("poiston jälkeen {} avainta", jarjestetty.size());
    // @loppu haku
}
