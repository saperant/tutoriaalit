// TSAN
// Atomiset operaatiot: lukottomuus, fetch_add, exchange,
// compare_exchange-silmukka ja atomic<double>.
#include <atomic>
#include <cstdint>
#include <print>
#include <thread>
#include <vector>

struct Pari {
    std::int32_t a;
    std::int32_t b;
};
struct Iso {
    std::int64_t arvot[3];
};

// @alku maksimi
// Atominen maksimi: lue, laske, yritä vaihtaa; toista, jos joku muu
// ehti väliin. compare_exchange_weak päivittää 'nyt'-arvon epäonnistuessa.
void paivita_maksimi(std::atomic<int>& maksimi, int arvo)
{
    int nyt = maksimi.load(std::memory_order_relaxed);
    while (nyt < arvo &&
           !maksimi.compare_exchange_weak(nyt, arvo,
                                          std::memory_order_relaxed)) {
    }
}
// @loppu maksimi

int main()
{
    // @alku lukottomuus
    std::println("int lukoton: {}", std::atomic<int>::is_always_lock_free);
    std::println("osoitin lukoton: {}",
                 std::atomic<void*>::is_always_lock_free);
    std::println("8-tavuinen rakenne lukoton: {}",
                 std::atomic<Pari>::is_always_lock_free);
    std::println("24-tavuinen rakenne lukoton: {}",
                 std::atomic<Iso>::is_always_lock_free);
    // @loppu lukottomuus

    // @alku operaatiot
    std::atomic<std::uint64_t> pyynnot{0};
    std::atomic<int> maksimi{0};
    std::atomic<double> summa{0.0};
    std::atomic<int> viimeisin{-1};
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < 4; ++s) {
            saikeet.emplace_back([&, s] {
                for (int i = 0; i < 10'000; ++i) {
                    // Pelkkä laskuri: järjestystä ei tarvita.
                    pyynnot.fetch_add(1, std::memory_order_relaxed);
                    paivita_maksimi(maksimi, (i * 7919 + s) % 100'003);
                    summa.fetch_add(0.5);          // C++20
                }
                (void)viimeisin.exchange(s);       // palauttaa vanhan
            });
        }
    }
    std::println("pyyntoja {}, maksimi {}, summa {}", pyynnot.load(),
                 maksimi.load(), summa.load());
    std::println("viimeisin on jokin saikeista: {}",
                 viimeisin.load() >= 0 && viimeisin.load() < 4 ? "kylla"
                                                               : "ei");
    // @loppu operaatiot
}
