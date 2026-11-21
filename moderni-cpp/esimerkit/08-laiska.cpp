#include <print>
#include <ranges>

int main()
{
    // @alku laiska
    auto nakyma = std::views::iota(1)
                  | std::views::transform([](int x) {
                        std::println("  lasketaan {}", x);
                        return x * 10;
                    })
                  | std::views::take(3);

    std::println("näkymä luotu");
    for (int x : nakyma) {
        std::println("saatiin {}", x);
    }
    // @loppu laiska
}
