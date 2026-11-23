#include <print>
#include <string>
#include <string_view>

std::string hae_nimi()
{
    return "Margaret Heafield Hamilton";
}

// Palauttaa näkymän parametrin sisältöön: kutsujan on pidettävä
// merkkijono elossa niin kauan kuin näkymää käytetään.
std::string_view sukunimi(const std::string& koko_nimi)
{
    return std::string_view{koko_nimi}.substr(koko_nimi.rfind(' ') + 1);
}

int main()
{
    // hae_nimi() palauttaa väliaikaisen merkkijonon, joka tuhoutuu
    // lausekkeen lopussa. Näkymä jää osoittamaan vapautettuun muistiin.
    std::string_view suku = sukunimi(hae_nimi());
    std::println("{}", suku);
}
