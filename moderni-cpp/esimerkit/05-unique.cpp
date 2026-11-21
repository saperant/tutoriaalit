#include <memory>
#include <print>
#include <string>
#include <utility>

struct Asiakas {
    std::string nimi;
    int id;
};

// @alku tehdas
std::unique_ptr<Asiakas> luo_asiakas(std::string nimi, int id)
{
    return std::make_unique<Asiakas>(std::move(nimi), id);
}
// @loppu tehdas

// @alku lainaus
// Ei omista: saa olion lainaksi viittauksena.
void tulosta(const Asiakas& a)
{
    std::println("#{} {}", a.id, a.nimi);
}

// Ottaa omistuksen: parametri on unique_ptr arvona.
void arkistoi(std::unique_ptr<Asiakas> a)
{
    std::println("arkistoitu {}", a->nimi);
}   // olio tuhoutuu tässä
// @loppu lainaus

int main()
{
    // @alku kaytto
    auto asiakas = luo_asiakas("Ada", 1);
    tulosta(*asiakas);

    arkistoi(std::move(asiakas));   // omistus siirtyy
    std::println("asiakas on tyhjä: {}", asiakas == nullptr);
    // @loppu kaytto
}
