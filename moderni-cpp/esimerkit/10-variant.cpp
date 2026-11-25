#include <numbers>
#include <print>
#include <variant>
#include <vector>

// @alku tyypit
struct Ympyra { double sade; };
struct Nelio { double sivu; };
struct Kolmio { double kanta, korkeus; };

using Muoto = std::variant<Ympyra, Nelio, Kolmio>;
// @loppu tyypit

// @alku kuormitus
template <typename... Funktiot>
struct Kuormitus : Funktiot... {
    using Funktiot::operator()...;
};
// @loppu kuormitus

// @alku ala
double ala(const Muoto& m)
{
    return std::visit(Kuormitus{
        [](const Ympyra& y) { return std::numbers::pi * y.sade * y.sade; },
        [](const Nelio& n) { return n.sivu * n.sivu; },
        [](const Kolmio& k) { return k.kanta * k.korkeus / 2; },
    }, m);
}
// @loppu ala

int main()
{
    // @alku kaytto
    std::vector<Muoto> muodot{Ympyra{1.0}, Nelio{2.0}, Kolmio{3.0, 4.0}};
    for (const auto& m : muodot) {
        std::println("indeksi {}, ala {:.2f}", m.index(), ala(m));
    }

    Muoto m = Nelio{5.0};
    if (const auto* n = std::get_if<Nelio>(&m)) {
        std::println("neliön sivu on {}", n->sivu);
    }
    m = Ympyra{0.5};   // variantti vaihtaa tyyppiä
    std::println("onko neliö: {}", std::holds_alternative<Nelio>(m));
    // @loppu kaytto
}
