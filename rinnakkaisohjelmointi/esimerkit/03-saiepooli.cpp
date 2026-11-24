// TSAN
// Säiepoolin käyttö: alkulukujen laskenta lohkoittain, tulokset ja
// virheet futureista lähetysjärjestyksessä.
#include <cstdint>
#include <future>
#include <print>
#include <stdexcept>
#include <vector>

#include "yhteinen/saiepooli.hpp"

int alkulukuja(std::uint32_t alku, std::uint32_t loppu)
{
    if (alku > loppu) {
        throw std::invalid_argument("tyhja vali");
    }
    int maara = 0;
    for (std::uint32_t n = alku < 2 ? 2 : alku; n < loppu; ++n) {
        bool alkuluku = true;
        for (std::uint32_t d = 2; d * d <= n; ++d) {
            if (n % d == 0) {
                alkuluku = false;
                break;
            }
        }
        maara += alkuluku ? 1 : 0;
    }
    return maara;
}

int main()
{
    // @alku kaytto
    constexpr std::uint32_t lohko = 25'000;
    std::vector<std::future<int>> tulokset;
    std::future<int> virheellinen;
    int yhteensa = 0;
    {
        Saiepooli pooli{3};
        for (std::uint32_t i = 0; i < 8; ++i) {
            tulokset.push_back(pooli.laheta([i] {
                return alkulukuja(i * lohko, (i + 1) * lohko);
            }));
        }
        virheellinen = pooli.laheta([] { return alkulukuja(10, 5); });

        for (std::size_t i = 0; i < tulokset.size(); ++i) {
            const int n = tulokset[i].get();     // odottaa tarvittaessa
            std::println("lohko {}: {} alkulukua", i, n);
            yhteensa += n;
        }
    }   // pooli suljettu: työntekijät ovat valmiita
    std::println("yhteensa alle {}: {}", 8 * lohko, yhteensa);
    try {
        (void)virheellinen.get();
    } catch (const std::invalid_argument& e) {
        std::println("virhe valittyi futuren kautta: {}", e.what());
    }
    // @loppu kaytto
}
