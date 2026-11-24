// TSAN
// Stressitesti: sama lyhyt rinnakkainen testi ajetaan monta kierrosta,
// säikeet lähtevät yhtä aikaa, ja satunnaiset yield-kutsut sekoittavat
// lomitusta. Jokaisen kierroksen lopuksi tarkistetaan invariantti.
#include <atomic>
#include <cstdint>
#include <functional>
#include <latch>
#include <mutex>
#include <print>
#include <random>
#include <thread>
#include <vector>

// @alku hairio
// Häiriö: satunnaisesti luovuta suoritin. Siemen on kiinteä, mutta
// lomitus riippuu silti vuorontajasta: stressitesti ei ole toistettava,
// joten löydetty virhe kannattaa toistaa ThreadSanitizerilla tai
// pienentää deterministiseksi testiksi.
class Hairio {
public:
    explicit Hairio(std::uint32_t siemen) : satunnainen_{siemen} {}
    void operator()()
    {
        if (satunnainen_() % 4 == 0) {
            std::this_thread::yield();
        }
    }

private:
    std::minstd_rand satunnainen_;
};
// @loppu hairio

// @alku ajuri
// Palauttaa kierrokset, joilla invariantti ei pitänyt.
int stressaa(int kierroksia, int saikeita,
             const std::function<void(int, Hairio&)>& runko,
             const std::function<bool()>& invariantti,
             const std::function<void()>& nollaa)
{
    int rikki = 0;
    for (int k = 0; k < kierroksia; ++k) {
        nollaa();
        std::latch lahto{saikeita};
        {
            std::vector<std::jthread> t;
            for (int s = 0; s < saikeita; ++s) {
                t.emplace_back([&, s] {
                    Hairio hairio{static_cast<std::uint32_t>(k * 97 + s)};
                    lahto.arrive_and_wait();   // kaikki liikkeelle yhtä aikaa
                    runko(s, hairio);
                });
            }
        }
        rikki += invariantti() ? 0 : 1;
    }
    return rikki;
}
// @loppu ajuri

int main()
{
    // @alku kaytto
    // Testattava: kaksi tiliä, siirrot molempiin suuntiin yhdellä lukolla.
    std::mutex lukko;
    long a = 0;
    long b = 0;
    const int rikki = stressaa(
        200, 4,
        [&](int s, Hairio& hairio) {
            for (int i = 0; i < 50; ++i) {
                hairio();
                std::scoped_lock l{lukko};
                const long summa = (s % 2 == 0) ? 3 : -3;
                a -= summa;
                hairio();                // lomitus kesken päivityksen
                b += summa;
            }
        },
        [&] { return a + b == 0; },
        [&] { a = b = 0; });
    std::println("200 kierrosta, invariantti rikki {} kierroksella", rikki);
    // @loppu kaytto
}
