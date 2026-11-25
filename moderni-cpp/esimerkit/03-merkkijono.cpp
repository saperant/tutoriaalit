#include <print>
#include <string>

int main()
{
    // @alku perus
    std::string nimi = "Ada";
    std::string tervehdys = "Hei, " + nimi;   // yhdistäminen
    tervehdys += "!";                         // kasvaa tarpeen mukaan
    std::println("{} ({} merkkiä)", tervehdys, tervehdys.size());
    // @loppu perus

    // @alku arvo
    std::string kopio = nimi;   // itsenäinen kopio, ei osoitin samaan
    kopio[0] = 'I';
    std::println("{} {} {}", nimi, kopio, nimi == kopio);
    std::println("{}", nimi < kopio);   // aakkosjärjestys
    // @loppu arvo

    // @alku haku
    std::string polku = "data/mittaukset.csv";
    auto kauttaviiva = polku.find('/');
    if (kauttaviiva != std::string::npos) {
        std::println("hakemisto: {}", polku.substr(0, kauttaviiva));
        std::println("tiedosto:  {}", polku.substr(kauttaviiva + 1));
    }
    std::println("csv: {}", polku.ends_with(".csv"));
    // @loppu haku

    // @alku muunnos
    int n = std::stoi("42");
    std::string teksti = std::to_string(n + 1);
    std::println("{} {}", n, teksti);
    // @loppu muunnos
}
