// TSAN
// Treiberin pino: lukoton pino yhdellä atomisella osoittimella.
// Poistettuja solmuja ei vapauteta ennen kuin kaikki säikeet ovat
// valmiita; muistin takaisinotto on oma ongelmansa (luku 9).
#include <atomic>
#include <cstdint>
#include <print>
#include <thread>
#include <vector>

// @alku pino
template <class T>
class Pino {
public:
    struct Solmu {
        T arvo;
        Solmu* seuraava = nullptr;
    };

    void laita(Solmu* uusi)
    {
        uusi->seuraava = paa_.load(std::memory_order_relaxed);
        // Epäonnistuessaan CAS kirjoittaa nykyisen pään uusi->seuraavaan.
        while (!paa_.compare_exchange_weak(uusi->seuraava, uusi,
                                           std::memory_order_release,
                                           std::memory_order_relaxed)) {
        }
    }

    Solmu* ota()
    {
        Solmu* vanha = paa_.load(std::memory_order_acquire);
        while (vanha != nullptr &&
               !paa_.compare_exchange_weak(vanha, vanha->seuraava,
                                           std::memory_order_acquire,
                                           std::memory_order_acquire)) {
        }
        return vanha;   // kutsuja omistaa solmun, mutta ei saa vielä
    }                   // vapauttaa sitä: toinen säie voi lukea sitä

private:
    std::atomic<Solmu*> paa_{nullptr};
};
// @loppu pino

int main()
{
    // @alku kaytto
    using P = Pino<std::uint64_t>;
    P pino;
    constexpr int saikeita = 4;
    constexpr std::uint64_t per_saie = 20'000;
    std::vector<std::vector<P::Solmu*>> otetut(saikeita);
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < saikeita; ++s) {
            saikeet.emplace_back([&pino, &otetut, s] {
                auto& omat = otetut[static_cast<std::size_t>(s)];
                for (std::uint64_t i = 1; i <= per_saie; ++i) {
                    pino.laita(new P::Solmu{i, nullptr});
                    if (i % 2 == 0) {          // ota joka toinen kerta
                        if (P::Solmu* n = pino.ota()) {
                            omat.push_back(n);
                        }
                    }
                }
            });
        }
    }   // nyt kukaan ei enää lue solmuja
    std::uint64_t summa = 0;
    std::size_t maara = 0;
    for (auto& omat : otetut) {
        for (P::Solmu* n : omat) {
            summa += n->arvo;
            ++maara;
            delete n;
        }
    }
    while (P::Solmu* n = pino.ota()) {
        summa += n->arvo;
        ++maara;
        delete n;
    }
    std::println("solmuja {}, summa {} (odotettu {})", maara, summa,
                 saikeita * per_saie * (per_saie + 1) / 2);
    // @loppu kaytto
}
