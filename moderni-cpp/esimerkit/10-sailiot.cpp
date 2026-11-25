#include <map>
#include <print>
#include <string>
#include <unordered_map>
#include <vector>

int main()
{
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
