#include <memory>
#include <print>
#include <string>
#include <utility>

int main()
{
    // @alku arvo-viittaus
    int laskuri = 0;
    auto kopio = [laskuri] { return laskuri; };   // arvo talteen nyt
    auto viite = [&laskuri] { return laskuri; };  // viittaus muuttujaan
    laskuri = 5;
    std::println("kopio: {}, viite: {}", kopio(), viite());
    // @loppu arvo-viittaus

    // @alku mutable
    auto seuraava = [n = 0]() mutable { return ++n; };
    int a = seuraava();
    int b = seuraava();
    int c = seuraava();
    std::println("{} {} {}", a, b, c);
    // @loppu mutable

    // @alku siirto
    auto viesti = std::make_unique<std::string>("siirretty lambdaan");
    auto tulosta = [v = std::move(viesti)] { std::println("{}", *v); };
    tulosta();
    std::println("viesti on nyt tyhjä: {}", viesti == nullptr);
    // @loppu siirto
}
