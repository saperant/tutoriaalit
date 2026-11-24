// Poikkeusten hinta: onnistuva ja epäonnistuva jäsennys.
#include <charconv>
#include <cstddef>
#include <expected>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "mittari.hpp"

// @alku poikkeus
// Heittää poikkeuksen, jos merkkijono ei ole kokonaisluku.
[[gnu::noinline]] int lue_poikkeus(std::string_view s)
{
    int arvo = 0;
    auto [loppu, virhe] = std::from_chars(s.data(), s.data() + s.size(),
                                          arvo);
    if (virhe != std::errc{} || loppu != s.data() + s.size()) {
        throw std::invalid_argument{"ei kokonaisluku"};
    }
    return arvo;
}
// @loppu poikkeus

// @alku expected
enum class Virhe { ei_luku, ylivuoto };

// Palauttaa virheen arvona: kutsuja tarkistaa tuloksen.
[[gnu::noinline]] std::expected<int, Virhe> lue_expected(std::string_view s)
{
    int arvo = 0;
    auto [loppu, virhe] = std::from_chars(s.data(), s.data() + s.size(),
                                          arvo);
    if (virhe == std::errc::result_out_of_range) {
        return std::unexpected{Virhe::ylivuoto};
    }
    if (virhe != std::errc{} || loppu != s.data() + s.size()) {
        return std::unexpected{Virhe::ei_luku};
    }
    return arvo;
}
// @loppu expected

// @alku summat
struct Tulos {
    long summa = 0;
    int virheita = 0;
};

Tulos summa_poikkeus(const std::vector<std::string>& rivit)
{
    Tulos t;
    for (const auto& r : rivit) {
        try {
            t.summa += lue_poikkeus(r);
        } catch (const std::invalid_argument&) {
            ++t.virheita;
        }
    }
    return t;
}

Tulos summa_expected(const std::vector<std::string>& rivit)
{
    Tulos t;
    for (const auto& r : rivit) {
        if (auto arvo = lue_expected(r)) {
            t.summa += *arvo;
        } else {
            ++t.virheita;
        }
    }
    return t;
}
// @loppu summat

std::vector<std::string> luo(std::size_t n, bool virheelliset)
{
    std::vector<std::string> rivit;
    for (std::size_t i = 0; i < n; ++i) {
        rivit.push_back(virheelliset ? "12x" : std::to_string(i % 1000));
    }
    return rivit;
}

template <typename Toimi>
void valitse(std::string_view tapa, const std::vector<std::string>& ok,
             const std::vector<std::string>& virheet, Toimi toimi)
{
    if (tapa == "poikkeus-ok") {
        toimi([&] { mittari::pida(summa_poikkeus(ok)); });
    } else if (tapa == "expected-ok") {
        toimi([&] { mittari::pida(summa_expected(ok)); });
    } else if (tapa == "poikkeus-virhe") {
        toimi([&] { mittari::pida(summa_poikkeus(virheet)); });
    } else if (tapa == "expected-virhe") {
        toimi([&] { mittari::pida(summa_expected(virheet)); });
    }
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    std::size_t n = tila.mittaa ? 100'000 : 1000;
    auto ok = luo(n, false);
    auto virheet = luo(n, true);
    if (tila.mittaa) {
        std::printf("jasennys, %zu rivia\n", n);
        for (std::string_view t : {"poikkeus-ok", "expected-ok",
                                   "poikkeus-virhe", "expected-virhe"}) {
            valitse(t, ok, virheet, [&](auto f) {
                mittari::tulosta(t, mittari::mittaa(f, 11));
            });
        }
        return 0;
    }
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, ok, virheet, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    for (const auto* rivit : {&ok, &virheet}) {
        Tulos p = summa_poikkeus(*rivit);
        Tulos e = summa_expected(*rivit);
        std::printf("poikkeus: summa %ld, virheita %d; "
                    "expected: summa %ld, virheita %d\n",
                    p.summa, p.virheita, e.summa, e.virheita);
    }
    auto iso = lue_expected("99999999999");
    std::printf("ylivuoto tunnistettu: %s\n",
                !iso && iso.error() == Virhe::ylivuoto ? "kylla" : "ei");
}
