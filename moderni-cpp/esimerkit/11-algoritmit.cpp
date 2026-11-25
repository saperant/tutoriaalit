#include <algorithm>
#include <print>
#include <string>
#include <vector>

// @alku tyyppi
struct Henkilo {
    std::string nimi;
    int ika;
};
// @loppu tyyppi

int main()
{
    // @alku projektio
    std::vector<Henkilo> ihmiset{
        {"Ada", 36}, {"Bjarne", 75}, {"Grace", 85}, {"Linus", 56}};

    std::ranges::sort(ihmiset, {}, &Henkilo::ika);
    for (const auto& h : ihmiset) {
        std::print("{} ", h.nimi);
    }
    std::println("");

    auto vanhin = std::ranges::max_element(ihmiset, {}, &Henkilo::ika);
    std::println("vanhin: {}", vanhin->nimi);

    auto loytyi = std::ranges::find(ihmiset, "Linus", &Henkilo::nimi);
    if (loytyi != ihmiset.end()) {
        std::println("Linus on {}-vuotias", loytyi->ika);
    }
    // @loppu projektio

    // @alku muut
    std::vector<int> luvut{4, 8, 15, 16, 23, 42};
    bool kaikki_positiivisia =
        std::ranges::all_of(luvut, [](int x) { return x > 0; });
    auto [pienin, suurin] = std::ranges::minmax(luvut);
    std::println("{} {} {}", kaikki_positiivisia, pienin, suurin);
    // @loppu muut
}
