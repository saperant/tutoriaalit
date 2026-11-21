#include <algorithm>
#include <functional>
#include <print>
#include <string>
#include <vector>

// @alku tehdas
auto tee_kertoja(int kerroin)
{
    return [kerroin](int x) { return x * kerroin; };
}
// @loppu tehdas

int main()
{
    // @alku perus
    auto nelio = [](int x) { return x * x; };
    std::println("{}", nelio(7));
    // @loppu perus

    // @alku algoritmi
    std::vector<int> luvut{5, -3, 8, -1, 4};
    auto negatiivisia = std::ranges::count_if(
        luvut, [](int x) { return x < 0; });
    std::println("negatiivisia: {}", negatiivisia);

    std::ranges::sort(luvut, [](int a, int b) { return a > b; });
    std::println("{} {} {} {} {}",
                 luvut[0], luvut[1], luvut[2], luvut[3], luvut[4]);
    // @loppu algoritmi

    // @alku yleinen
    auto suurempi = [](const auto& a, const auto& b) {
        return a > b ? a : b;
    };
    std::println("{} {}", suurempi(3, 9),
                 suurempi(std::string{"kissa"}, std::string{"koira"}));
    // @loppu yleinen

    // @alku sulkeuma
    auto tuplaa = tee_kertoja(2);
    auto kymmenkertaista = tee_kertoja(10);
    std::println("{} {}", tuplaa(21), kymmenkertaista(21));
    // @loppu sulkeuma

    // @alku function
    std::vector<std::function<int(int)>> muunnokset{
        nelio, tuplaa, [](int x) { return x + 1; }};
    for (const auto& f : muunnokset) {
        std::print("{} ", f(5));
    }
    std::println("");
    // @loppu function
}
