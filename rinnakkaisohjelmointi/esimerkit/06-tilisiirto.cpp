// TSAN
// Kahden lukon ottaminen: std::scoped_lock lukitsee molemmat tilit
// lukkiutumatta, vaikka siirtoja tehdään kumpaankin suuntaan.
#include <cstdint>
#include <mutex>
#include <print>
#include <random>
#include <thread>
#include <vector>

// @alku tili
struct Tili {
    std::mutex mutex;
    std::int64_t saldo = 1'000;
};

// Palauttaa false, jos kate ei riitä. Sama tili kahdesti lukitsisi
// saman mutexin kahdesti, joten se torjutaan ensin.
bool siirra(Tili& mista, Tili& minne, std::int64_t summa)
{
    if (&mista == &minne) {
        return false;
    }
    std::scoped_lock lukko{mista.mutex, minne.mutex};  // ei lukkiudu
    if (mista.saldo < summa) {
        return false;
    }
    mista.saldo -= summa;
    minne.saldo += summa;
    return true;
}
// @loppu tili

int main()
{
    // @alku kaytto
    std::vector<Tili> tilit(5);
    {
        std::vector<std::jthread> saikeet;
        for (unsigned s = 0; s < 4; ++s) {
            saikeet.emplace_back([&tilit, s] {
                std::mt19937 satunnainen{s};   // kiinteä siemen
                std::uniform_int_distribution<std::size_t> tili{0, 4};
                for (int i = 0; i < 20'000; ++i) {
                    (void)siirra(tilit[tili(satunnainen)],
                                 tilit[tili(satunnainen)],
                                 1 + i % 50);
                }
            });
        }
    }
    std::int64_t yhteensa = 0;
    bool negatiivisia = false;
    for (const Tili& t : tilit) {
        yhteensa += t.saldo;
        negatiivisia = negatiivisia || t.saldo < 0;
    }
    std::println("rahaa yhteensa {} (alussa 5000)", yhteensa);
    std::println("negatiivisia saldoja: {}", negatiivisia ? "on" : "ei");
    // @loppu kaytto
}
