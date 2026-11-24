// TSAN
// Rajattu estävä jono: tuottaja odottaa, kun jono on täynnä
// (vastapaine), ja kuluttaja, kun se on tyhjä.
#include <algorithm>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <mutex>
#include <optional>
#include <print>
#include <thread>
#include <utility>
#include <vector>

// @alku jono
template <class T>
class RajattuJono {
public:
    explicit RajattuJono(std::size_t kapasiteetti) : kap_{kapasiteetti} {}

    // Palauttaa false, jos jono on suljettu.
    bool laita(T arvo)
    {
        std::unique_lock lukko{mutex_};
        ei_taysi_.wait(lukko, [this] {
            return suljettu_ || alkiot_.size() < kap_;
        });
        if (suljettu_) {
            return false;
        }
        alkiot_.push_back(std::move(arvo));
        suurin_ = std::max(suurin_, alkiot_.size());
        lukko.unlock();
        ei_tyhja_.notify_one();       // ilmoitus lukon ulkopuolella
        return true;
    }

    // Tyhjä optional: jono on suljettu ja tyhjennetty.
    std::optional<T> ota()
    {
        std::unique_lock lukko{mutex_};
        ei_tyhja_.wait(lukko, [this] {
            return suljettu_ || !alkiot_.empty();
        });
        if (alkiot_.empty()) {
            return std::nullopt;
        }
        T arvo = std::move(alkiot_.front());
        alkiot_.pop_front();
        lukko.unlock();
        ei_taysi_.notify_one();
        return arvo;
    }

    void sulje()
    {
        {
            std::scoped_lock lukko{mutex_};
            suljettu_ = true;
        }
        ei_taysi_.notify_all();       // kaikki odottajat heräävät
        ei_tyhja_.notify_all();
    }

    std::size_t suurin_koko()
    {
        std::scoped_lock lukko{mutex_};
        return suurin_;
    }

private:
    std::mutex mutex_;
    std::condition_variable ei_taysi_;
    std::condition_variable ei_tyhja_;
    std::deque<T> alkiot_;
    std::size_t kap_;
    std::size_t suurin_ = 0;
    bool suljettu_ = false;
};
// @loppu jono

int main()
{
    // @alku kaytto
    RajattuJono<std::uint64_t> jono{8};
    std::vector<std::uint64_t> summat(3, 0);
    {
        std::vector<std::jthread> kuluttajat;
        for (std::size_t k = 0; k < summat.size(); ++k) {
            kuluttajat.emplace_back([&jono, &summat, k] {
                while (auto arvo = jono.ota()) {
                    summat[k] += *arvo;
                }
            });
        }
        {
            std::vector<std::jthread> tuottajat;
            for (std::uint64_t t = 0; t < 2; ++t) {
                tuottajat.emplace_back([&jono, t] {
                    for (std::uint64_t i = 1; i <= 50'000; ++i) {
                        (void)jono.laita(i * 2 + t);
                    }
                });
            }
        }   // tuottajat valmiita
        jono.sulje();
    }   // kuluttajat tyhjentävät jonon ja lopettavat
    std::uint64_t yhteensa = 0;
    for (auto s : summat) {
        yhteensa += s;
    }
    std::println("summa {} (odotettu {})", yhteensa,
                 2 * 50'000ull * 50'001ull + 50'000ull);
    std::println("jono enintaan {} alkiota: {}", 8,
                 jono.suurin_koko() <= 8 ? "kylla" : "ei");
    // @loppu kaytto
}
