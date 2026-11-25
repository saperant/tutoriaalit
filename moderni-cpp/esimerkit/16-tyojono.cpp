// TSAN
#include <atomic>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <optional>
#include <print>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

// @alku jono
// Suljettava työjono: tuottajat lisäävät töitä, kuluttajat ottavat niitä,
// ja sulkemisen jälkeen kuluttajat tyhjentävät jonon ja lopettavat.
template <typename T>
class Tyojono {
public:
    void lisaa(T tyo)
    {
        {
            std::scoped_lock lukko{mutex_};
            if (suljettu_) {
                throw std::logic_error{"työjono on suljettu"};
            }
            jono_.push_back(std::move(tyo));
        }
        ehto_.notify_one();   // herätetään yksi odottaja lukon ulkopuolella
    }

    void sulje()
    {
        {
            std::scoped_lock lukko{mutex_};
            suljettu_ = true;
        }
        ehto_.notify_all();
    }

    // Odottaa työtä. Palauttaa tyhjän, kun jono on suljettu ja tyhjä.
    std::optional<T> ota()
    {
        std::unique_lock lukko{mutex_};
        ehto_.wait(lukko, [this] { return suljettu_ || !jono_.empty(); });
        if (jono_.empty()) {
            return std::nullopt;
        }
        T tyo = std::move(jono_.front());
        jono_.pop_front();
        return tyo;
    }

private:
    std::mutex mutex_;
    std::condition_variable ehto_;
    std::deque<T> jono_;
    bool suljettu_ = false;
};
// @loppu jono

int main()
{
    // @alku kaytto
    Tyojono<int> jono;
    std::atomic<long long> summa{0};
    std::atomic<int> kasitelty{0};
    {
        std::vector<std::jthread> kuluttajat;
        for (int i = 0; i < 3; ++i) {
            kuluttajat.emplace_back([&jono, &summa, &kasitelty] {
                while (auto tyo = jono.ota()) {
                    summa += static_cast<long long>(*tyo) * *tyo;
                    ++kasitelty;
                }
            });
        }
        for (int i = 1; i <= 1000; ++i) {
            jono.lisaa(i);
        }
        jono.sulje();
    }   // kuluttajat tyhjentävät jonon ja jthread odottaa ne
    std::println("käsitelty {} työtä, neliöiden summa {}",
                 kasitelty.load(), summa.load());
    // @loppu kaytto
}
