// 16-bittiset sekvenssinumerot kiertävät 65535:stä nollaan. Vertailu
// "uudempi kuin" on tehtävä niin, että kierto ei sotke järjestystä.
#include <cstdint>
#include <print>

// @alku uudempi
// a on uudempi kuin b, jos se on enintään puoli kierrosta edellä.
constexpr bool uudempi(std::uint16_t a, std::uint16_t b) {
    return static_cast<std::int16_t>(static_cast<std::uint16_t>(a - b)) > 0;
}
// @loppu uudempi

constexpr bool naiivi(std::uint16_t a, std::uint16_t b) { return a > b; }

static_assert(uudempi(1, 0) && uudempi(0, 65535) && !uudempi(65535, 0));

int main() {
    const std::uint16_t parit[][2] = {
        {101, 100}, {100, 101}, {2, 65534}, {65534, 2}, {40000, 100}};
    for (const auto& p : parit) {
        std::println("{:>5} uudempi kuin {:>5}? oikein: {:<5} naiivi: {}",
                     p[0], p[1], uudempi(p[0], p[1]), naiivi(p[0], p[1]));
    }
    // 60 pakettia sekunnissa: kierros kestää 65536 / 60 s.
    std::println("kierros 60 Hz:llä: {} s", 65536 / 60);
}
