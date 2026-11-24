// TSAN
// Säikeen argumentit: kopio, viittaus std::refillä, siirto ja
// säiekohtainen muuttuja.
#include <functional>
#include <memory>
#include <print>
#include <string>
#include <thread>
#include <utility>
#include <vector>

// @alku funktiot
void kasvata(int& laskuri, int maara)
{
    laskuri += maara;
}

std::size_t pituus(std::unique_ptr<std::string> teksti)
{
    return teksti->size();     // säie omistaa merkkijonon
}
// @loppu funktiot

// @alku saiekohtainen
thread_local int kutsuja = 0;  // jokaisella säikeellä oma kopio

int laske_kutsut(int kertaa)
{
    for (int i = 0; i < kertaa; ++i) {
        ++kutsuja;
    }
    return kutsuja;
}
// @loppu saiekohtainen

int main()
{
    // @alku valitys
    int laskuri = 0;
    {
        // std::thread kopioi argumentit säikeen omaan tallennustilaan.
        // Viittaus on pyydettävä erikseen std::refillä.
        std::jthread s1{kasvata, std::ref(laskuri), 5};
    }
    std::println("laskuri std::refin jalkeen: {}", laskuri);

    auto teksti = std::make_unique<std::string>("rinnakkainen");
    std::size_t tulos = 0;
    {
        std::jthread s2{[&tulos](std::unique_ptr<std::string> t) {
            tulos = pituus(std::move(t));
        }, std::move(teksti)};
    }
    std::println("siirretty merkkijono: pituus {}, paaohjelmalla {}",
                 tulos, teksti ? "on" : "ei ole");
    // @loppu valitys

    // @alku tl-kaytto
    std::vector<int> tulokset(3);
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < 3; ++s) {
            saikeet.emplace_back([&tulokset, s] {
                tulokset[static_cast<std::size_t>(s)] =
                    laske_kutsut((s + 1) * 10);
            });
        }
    }
    std::println("saikeiden laskurit: {} {} {}", tulokset[0], tulokset[1],
                 tulokset[2]);
    std::println("paasaikeen laskuri: {}", kutsuja);
    // @loppu tl-kaytto
}
