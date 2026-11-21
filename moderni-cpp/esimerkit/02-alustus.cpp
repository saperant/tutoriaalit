#include <print>
#include <string>
#include <vector>

// @alku jasenet
struct Asetukset {
    std::string nimi = "oletus";  // jäsenen oletusarvo
    int leveys = 80;
    bool varit = true;
};
// @loppu jasenet

int main()
{
    // @alku aaltosulut
    int a{5};
    double b{2.5};
    std::string s{"teksti"};
    std::vector<int> v{1, 2, 3};
    int nolla{};          // arvoalustus: 0
    // @loppu aaltosulut
    std::println("{} {} {} {} {}", a, b, s, v.size(), nolla);

    // @alku sudenkuoppa
    std::vector<int> kaksi_alkiota{3, 1};   // alkiot 3 ja 1
    std::vector<int> kolme_ykkosta(3, 1);   // alkiot 1, 1 ja 1
    // @loppu sudenkuoppa
    std::println("{} {}", kaksi_alkiota.size(), kolme_ykkosta.size());

    // @alku nimetyt
    Asetukset oletus{};
    Asetukset leveat{.nimi = "leveä", .leveys = 120};
    // @loppu nimetyt
    std::println("{} {} {}", oletus.nimi, oletus.leveys, oletus.varit);
    std::println("{} {} {}", leveat.nimi, leveat.leveys, leveat.varit);
}
