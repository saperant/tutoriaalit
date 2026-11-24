// TSAN
// Vaiheittainen laskenta std::barrierilla: lämmön tasoittuminen sauvassa.
// Jokainen säie päivittää oman osansa, ja este erottaa askeleet.
// Valmistumisfunktio vaihtaa puskurit, kun kaikki ovat valmiita.
#include <barrier>
#include <cstddef>
#include <print>
#include <thread>
#include <utility>
#include <vector>

using Sauva = std::vector<double>;

// Yksi askel: jokainen sisäpiste kohti naapuriensa keskiarvoa.
void askel(const Sauva& vanha, Sauva& uusi, std::size_t alku,
           std::size_t loppu)
{
    for (std::size_t i = alku; i < loppu; ++i) {
        uusi[i] = vanha[i] + 0.25 * (vanha[i - 1] - 2 * vanha[i] +
                                     vanha[i + 1]);
    }
}

Sauva alkutila(std::size_t n)
{
    Sauva s(n, 0.0);
    s.front() = 100.0;            // vasen pää kuuma, oikea kylmä
    return s;
}

// @alku rinnakkainen
Sauva rinnakkain(std::size_t n, int askelia, std::size_t saikeita)
{
    Sauva a = alkutila(n);
    Sauva b = a;
    Sauva* vanha = &a;
    Sauva* uusi = &b;
    int tehty = 0;
    std::barrier este{static_cast<std::ptrdiff_t>(saikeita),
                      [&]() noexcept {
                          std::swap(vanha, uusi);   // yksi säie, muut
                          ++tehty;                  // odottavat
                      }};
    {
        std::vector<std::jthread> saikeet;
        const std::size_t sisapisteita = n - 2;
        for (std::size_t s = 0; s < saikeita; ++s) {
            const std::size_t alku = 1 + s * sisapisteita / saikeita;
            const std::size_t loppu = 1 + (s + 1) * sisapisteita / saikeita;
            saikeet.emplace_back([&, alku, loppu] {
                for (int k = 0; k < askelia; ++k) {
                    askel(*vanha, *uusi, alku, loppu);
                    este.arrive_and_wait();   // kaikki valmiita ennen
                }                             // seuraavaa askelta
            });
        }
    }
    std::println("askelia tehty {}", tehty);
    return *vanha;
}
// @loppu rinnakkainen

int main()
{
    constexpr std::size_t n = 202;
    constexpr int askelia = 4'000;
    // @alku vertailu
    Sauva sarja_a = alkutila(n);
    Sauva sarja_b = sarja_a;
    for (int k = 0; k < askelia; ++k) {
        askel(sarja_a, sarja_b, 1, n - 1);
        std::swap(sarja_a, sarja_b);
    }
    const Sauva tulos = rinnakkain(n, askelia, 3);
    std::println("rinnakkainen == sarjallinen (bitilleen): {}",
                 tulos == sarja_a ? "kylla" : "ei");
    std::println("lampotila kohdissa 10, 50, 100: {:.3f} {:.3f} {:.3f}",
                 tulos[10], tulos[50], tulos[100]);
    // @loppu vertailu
}
