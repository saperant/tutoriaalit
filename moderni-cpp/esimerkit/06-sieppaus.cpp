#include <memory>
#include <print>
#include <string>
#include <utility>

// @alku this
struct Mittari {
    int arvo = 0;

    // [this] sieppaa osoittimen olioon, [*this] kopion oliosta.
    auto viittaava() { return [this] { return arvo; }; }
    auto kopioiva() { return [*this] { return arvo; }; }
};
// @loppu this

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

    // @alku this-kaytto
    Mittari mittari{1};
    auto nykyinen = mittari.viittaava();
    auto tallennettu = mittari.kopioiva();
    mittari.arvo = 2;
    std::println("this: {}, *this: {}", nykyinen(), tallennettu());
    // @loppu this-kaytto
}
