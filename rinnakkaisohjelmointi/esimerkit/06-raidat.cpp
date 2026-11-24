// TSAN
// Lukkojen raidoitus (lock striping): hajautustaulu jaetaan osiin, ja
// jokaisella osalla on oma lukko. Eri osiin osuvat päivitykset eivät
// odota toisiaan.
#include <array>
#include <cstddef>
#include <functional>
#include <mutex>
#include <print>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

// @alku raidat
class Laskuritaulu {
public:
    void lisaa(const std::string& avain)
    {
        Raita& r = raita(avain);
        std::scoped_lock lukko{r.mutex};
        ++r.maarat[avain];
    }

    int hae(const std::string& avain)
    {
        Raita& r = raita(avain);
        std::scoped_lock lukko{r.mutex};
        const auto it = r.maarat.find(avain);
        return it == r.maarat.end() ? 0 : it->second;
    }

    // Koko taulun operaatio ottaa kaikki lukot aina samassa järjestyksessä.
    std::size_t koko()
    {
        std::size_t n = 0;
        for (Raita& r : raidat_) {
            std::scoped_lock lukko{r.mutex};
            n += r.maarat.size();
        }
        return n;
    }

private:
    struct Raita {
        std::mutex mutex;
        std::unordered_map<std::string, int> maarat;
    };

    Raita& raita(const std::string& avain)
    {
        return raidat_[std::hash<std::string>{}(avain) % raidat_.size()];
    }

    std::array<Raita, 16> raidat_;
};
// @loppu raidat

int main()
{
    // @alku kaytto
    Laskuritaulu taulu;
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < 4; ++s) {
            saikeet.emplace_back([&taulu, s] {
                for (int i = 0; i < 25'000; ++i) {
                    taulu.lisaa("sana" + std::to_string((i * 31 + s) % 1000));
                }
            });
        }
    }
    std::println("eri sanoja {}", taulu.koko());
    std::println("sana0: {}, sana999: {}", taulu.hae("sana0"),
                 taulu.hae("sana999"));
    // @loppu kaytto
}
