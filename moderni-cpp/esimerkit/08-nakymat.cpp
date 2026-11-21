#include <print>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

int main()
{
    // @alku putki
    std::vector<int> luvut{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    auto parillisten_neliot =
        luvut
        | std::views::filter([](int x) { return x % 2 == 0; })
        | std::views::transform([](int x) { return x * x; });

    for (int x : parillisten_neliot) {
        std::print("{} ", x);
    }
    std::println("");
    // @loppu putki

    // @alku tehtaat
    for (int x : std::views::iota(1) | std::views::take(5)
                     | std::views::reverse) {
        std::print("{} ", x);
    }
    std::println("");
    // @loppu tehtaat

    // @alku to
    auto kopio = std::ranges::to<std::vector>(parillisten_neliot);
    std::println("vektorissa {} alkiota", kopio.size());
    // @loppu to

    // @alku cpp23
    std::vector<std::string> nimet{"Ada", "Bjarne", "Grace"};
    std::vector<int> vuodet{1815, 1950, 1906};

    for (auto [i, nimi] : std::views::enumerate(nimet)) {
        std::println("{}. {}", i + 1, nimi);
    }
    for (auto [nimi, vuosi] : std::views::zip(nimet, vuodet)) {
        std::println("{} syntyi {}", nimi, vuosi);
    }
    for (auto pala : std::views::iota(1, 8) | std::views::chunk(3)) {
        std::print("[");
        for (int x : pala) {
            std::print(" {}", x);
        }
        std::print(" ] ");
    }
    std::println("");
    // @loppu cpp23

    // @alku split
    std::string_view lause = "laiska kettu hyppää";
    for (auto sana : std::views::split(lause, ' ')) {
        std::println("'{}'", std::string_view{sana});
    }
    // @loppu split
}
