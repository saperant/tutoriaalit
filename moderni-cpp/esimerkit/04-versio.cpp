#include <algorithm>
#include <compare>
#include <format>
#include <print>
#include <vector>

// @alku luokka
struct Versio {
    int paa = 0;
    int sivu = 0;
    int korjaus = 0;

    // Kääntäjä tuottaa vertailut jäsenten esittelyjärjestyksessä.
    auto operator<=>(const Versio&) const = default;
};
// @loppu luokka

// @alku muotoilija
template <>
struct std::formatter<Versio> : std::formatter<std::string> {
    auto format(const Versio& v, std::format_context& ctx) const
    {
        return std::formatter<std::string>::format(
            std::format("{}.{}.{}", v.paa, v.sivu, v.korjaus), ctx);
    }
};
// @loppu muotoilija

int main()
{
    // @alku kaytto
    Versio a{1, 4, 2};
    Versio b{1, 10, 0};
    std::println("{} < {}: {}", a, b, a < b);
    std::println("{} == {}: {}", a, a, a == Versio{1, 4, 2});

    std::vector<Versio> versiot{{2, 0, 0}, {1, 10, 0}, {1, 4, 2}};
    std::ranges::sort(versiot);
    for (const auto& v : versiot) {
        std::println("{:>8}", v);
    }
    // @loppu kaytto
}
