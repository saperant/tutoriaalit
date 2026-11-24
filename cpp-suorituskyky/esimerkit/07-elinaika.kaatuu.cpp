// Näkymä vektorin alkioon jää roikkumaan, kun vektori kasvaa.
#include <cstdio>
#include <string>
#include <string_view>
#include <vector>

int main()
{
    // @alku roikkuva
    std::vector<std::string> sanat{"alfa", "beta"};
    // Lyhyt merkkijono on std::stringin sisällä (SSO), siis vektorin
    // puskurissa. Näkymä osoittaa suoraan sinne.
    std::string_view ensimmainen = sanat.front();
    sanat.push_back("gamma");   // uusi puskuri, vanha vapautetaan
    std::string kopio{ensimmainen};   // lukee vapautettua muistia
    std::printf("%s\n", kopio.c_str());
    // @loppu roikkuva
}
