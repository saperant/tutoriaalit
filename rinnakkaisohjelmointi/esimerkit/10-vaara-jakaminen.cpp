// TSAN
// Väärä jakaminen: säikeet kasvattavat kukin omaa laskuriaan, mutta
// vierekkäiset laskurit ovat samalla välimuistirivillä. Ajat
// tulostetaan virhetulosteeseen, koska ne riippuvat koneesta.
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <new>
#include <print>
#include <string_view>
#include <thread>
#include <vector>

// @alku rakenteet
struct Tiivis {
    std::atomic<std::uint64_t> n{0};
};

struct alignas(std::hardware_destructive_interference_size) Erillinen {
    std::atomic<std::uint64_t> n{0};
};
// @loppu rakenteet

template <class Laskuri>
std::uint64_t kilpaile(std::string_view nimi)
{
    std::array<Laskuri, 4> laskurit{};
    const auto alku = std::chrono::steady_clock::now();
    {
        std::vector<std::jthread> t;
        for (std::size_t s = 0; s < laskurit.size(); ++s) {
            t.emplace_back([&laskurit, s] {
                for (int i = 0; i < 1'000'000; ++i) {
                    laskurit[s].n.fetch_add(1, std::memory_order_relaxed);
                }
            });
        }
    }
    const std::chrono::duration<double, std::milli> kesto =
        std::chrono::steady_clock::now() - alku;
    std::print(stderr, "{}: {:.1f} ms\n", nimi, kesto.count());
    std::uint64_t summa = 0;
    for (const auto& l : laskurit) {
        summa += l.n.load();
    }
    return summa;
}

int main()
{
    // @alku kaytto
    std::println("valimuistirivi {} tavua",
                 std::hardware_destructive_interference_size);
    std::println("tiivis: laskuri {} tavua, nelja laskuria {} tavua",
                 sizeof(Tiivis), sizeof(std::array<Tiivis, 4>));
    std::println("erillinen: laskuri {} tavua", sizeof(Erillinen));
    const auto a = kilpaile<Tiivis>("tiivis");
    const auto b = kilpaile<Erillinen>("erillinen");
    std::println("summat {} ja {}", a, b);
    // @loppu kaytto
}
