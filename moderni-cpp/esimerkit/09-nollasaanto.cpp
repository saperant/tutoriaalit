#include <print>
#include <string>
#include <utility>
#include <vector>

// @alku nolla
class Soittolista {
public:
    explicit Soittolista(std::string nimi) : nimi_{std::move(nimi)} {}

    // Arvoparametri + siirto: toimii tehokkaasti sekä kopioitaville
    // että siirrettäville argumenteille.
    void lisaa(std::string kappale)
    {
        kappaleet_.push_back(std::move(kappale));
    }

    const std::string& nimi() const { return nimi_; }
    const std::vector<std::string>& kappaleet() const { return kappaleet_; }

private:
    std::string nimi_;
    std::vector<std::string> kappaleet_;
};
// @loppu nolla

int main()
{
    // @alku kaytto
    Soittolista lista{"Suosikit"};
    std::string kappale = "Finlandia";
    lista.lisaa(kappale);              // kopioidaan: kappale säilyy
    lista.lisaa("Kullervo");           // väliaikainen: ei kopiota
    std::println("{}: {} kappaletta", lista.nimi(),
                 lista.kappaleet().size());

    const auto* ennen = lista.kappaleet().data();
    Soittolista siirretty = std::move(lista);
    const auto* jalkeen = siirretty.kappaleet().data();
    std::println("alkiot pysyivät paikallaan: {}", ennen == jalkeen);
    // @loppu kaytto
}
