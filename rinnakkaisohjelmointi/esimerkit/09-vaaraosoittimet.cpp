// TSAN
// Treiberin pino vaaraosoittimilla (hazard pointers): solmu vapautetaan
// vasta, kun mikään säie ei ilmoita käyttävänsä sitä.
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <optional>
#include <print>
#include <thread>
#include <vector>

constexpr std::size_t max_saikeita = 4;

// @alku pino
class Pino {
public:
    struct Solmu {
        std::uint64_t arvo;
        Solmu* seuraava;
    };

    void laita(std::uint64_t arvo)
    {
        Solmu* uusi = new Solmu{arvo, paa_.load()};
        while (!paa_.compare_exchange_weak(uusi->seuraava, uusi)) {
        }
    }

    // s on kutsuvan säikeen numero 0..max_saikeita-1.
    std::optional<std::uint64_t> ota(std::size_t s)
    {
        std::atomic<Solmu*>& vaara = vaarat_[s];
        for (;;) {
            Solmu* p = paa_.load();
            if (p == nullptr) {
                return std::nullopt;
            }
            vaara.store(p);              // "käytän solmua p"
            if (paa_.load() != p) {
                continue;                // p ehti poistua: yritä uudelleen
            }
            // Nyt p ei voi vapautua: jokainen poistaja näkee ilmoituksen.
            if (paa_.compare_exchange_strong(p, p->seuraava)) {
                vaara.store(nullptr);
                const std::uint64_t arvo = p->arvo;
                poista_myohemmin(s, p);
                return arvo;
            }
        }
    }
// @loppu pino

// @alku vapautus
    ~Pino()       // kutsutaan, kun säikeet ovat valmiita
    {
        for (auto& lista : poistettavat_) {
            for (Solmu* p : lista) {
                delete p;
            }
        }
        while (Solmu* p = paa_.load()) {
            paa_.store(p->seuraava);
            delete p;
        }
    }

    std::uint64_t vapautettu() const { return vapautettu_.load(); }

private:
    void poista_myohemmin(std::size_t s, Solmu* p)
    {
        auto& lista = poistettavat_[s];
        lista.push_back(p);
        if (lista.size() < 2 * max_saikeita) {
            return;                       // kerätään erä kerrallaan
        }
        std::array<Solmu*, max_saikeita> kaytossa{};
        for (std::size_t i = 0; i < max_saikeita; ++i) {
            kaytossa[i] = vaarat_[i].load();
        }
        std::erase_if(lista, [&](Solmu* q) {
            if (std::ranges::find(kaytossa, q) != kaytossa.end()) {
                return false;             // joku käyttää: säilytä
            }
            delete q;
            vapautettu_.fetch_add(1, std::memory_order_relaxed);
            return true;
        });
    }

    std::atomic<Solmu*> paa_{nullptr};
    std::array<std::atomic<Solmu*>, max_saikeita> vaarat_{};
    std::array<std::vector<Solmu*>, max_saikeita> poistettavat_;
    std::atomic<std::uint64_t> vapautettu_{0};
};
// @loppu vapautus

int main()
{
    // @alku kaytto
    std::atomic<std::uint64_t> summa{0};
    std::uint64_t vapautettu = 0;
    {
        Pino pino;
        {
            std::vector<std::jthread> saikeet;
            for (std::size_t s = 0; s < max_saikeita; ++s) {
                saikeet.emplace_back([&pino, &summa, s] {
                    for (std::uint64_t i = 1; i <= 20'000; ++i) {
                        pino.laita(i);
                        if (auto arvo = pino.ota(s)) {
                            summa.fetch_add(*arvo);
                        }
                    }
                });
            }
        }
        vapautettu = pino.vapautettu();
    }   // pinon hajotin vapauttaa loput
    std::println("summa {} (odotettu {})", summa.load(),
                 max_saikeita * 20'000ull * 20'001ull / 2);
    // Kunkin säikeen listaan jää alle 2 * max_saikeita solmua.
    std::println("vapauttamatta ajon lopussa enintaan {}: {}",
                 2 * max_saikeita * max_saikeita,
                 80'000 - vapautettu <= 2 * max_saikeita * max_saikeita
                     ? "kylla" : "ei");
    // @loppu kaytto
}
