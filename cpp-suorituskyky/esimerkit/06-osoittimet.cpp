// Älykkäiden osoittimien hinta: varaukset, koko ja viitelaskurin
// päivitykset.
#include <cstddef>
#include <cstdio>
#include <memory>
#include <span>
#include <string_view>

#include "laskuri.hpp"
#include "mittari.hpp"

struct Asetukset {
    int taso = 3;
    int raja = 100;
};

// @alku luonti
// Varaukset oliota kohden: unique_ptr yksi, shared_ptr(new T) kaksi
// (olio ja ohjauslohko erikseen), make_shared yksi (samassa lohkossa).
std::size_t varaukset_unique()
{
    laskuri::Jakso j;
    auto p = std::make_unique<Asetukset>();
    mittari::pida(p);
    return j.varaukset();
}

std::size_t varaukset_shared_new()
{
    laskuri::Jakso j;
    std::shared_ptr<Asetukset> p{new Asetukset};
    mittari::pida(p);
    return j.varaukset();
}

std::size_t varaukset_make_shared()
{
    laskuri::Jakso j;
    auto p = std::make_shared<Asetukset>();
    mittari::pida(p);
    return j.varaukset();
}
// @loppu luonti

// @alku valitys
// Arvona välitetty shared_ptr kopioidaan: viitelaskuria kasvatetaan
// kutsussa ja vähennetään paluussa, kumpikin atomisella operaatiolla.
[[gnu::noinline]] int lue_arvona(std::shared_ptr<const Asetukset> a)
{
    return a->taso;
}

// Viittaus ei koske laskuriin: funktio vain lukee, eikä se tarvitse
// omaa osuutta omistuksesta.
[[gnu::noinline]] int lue_viitteena(const std::shared_ptr<const Asetukset>& a)
{
    return a->taso;
}

// Paras rajapinta funktiolle, joka ei säilytä osoitinta: pelkkä
// viittaus olioon. Kutsuja voi omistaa olion millä tavalla tahansa.
[[gnu::noinline]] int lue_oliosta(const Asetukset& a) { return a.taso; }
// @loppu valitys

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    auto jaettu = std::make_shared<const Asetukset>();
    auto oma = std::make_unique<const Asetukset>();
    if (!tila.kerran.empty()) {
        auto toista = [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                mittari::piilota(jaettu);
                mittari::pida(f());
            }
        };
        if (tila.kerran == "arvona") {
            toista([&] { return lue_arvona(jaettu); });
        } else if (tila.kerran == "viitteena") {
            toista([&] { return lue_viitteena(jaettu); });
        } else if (tila.kerran == "oliosta") {
            toista([&] { return lue_oliosta(*jaettu); });
        }
        return 0;
    }
    // @alku testi
    std::printf("varauksia: make_unique %zu, shared_ptr(new) %zu, "
                "make_shared %zu\n",
                varaukset_unique(), varaukset_shared_new(),
                varaukset_make_shared());
    std::printf("koot: T* %zu, unique_ptr %zu, shared_ptr %zu tavua\n",
                sizeof(Asetukset*), sizeof(std::unique_ptr<Asetukset>),
                sizeof(std::shared_ptr<Asetukset>));
    long ennen = jaettu.use_count();
    int summa = lue_arvona(jaettu) + lue_viitteena(jaettu)
                + lue_oliosta(*oma);
    std::printf("summa %d, viitteita ennen %ld ja jalkeen %ld\n", summa,
                ennen, jaettu.use_count());
    // @loppu testi
}
