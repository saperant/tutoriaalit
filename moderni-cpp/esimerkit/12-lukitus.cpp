// TSAN
#include <atomic>
#include <format>
#include <mutex>
#include <print>
#include <string>
#include <thread>
#include <utility>
#include <vector>

// @alku mutex
class Loki {
public:
    void kirjaa(std::string viesti)
    {
        std::scoped_lock lukko{mutex_};   // vapautuu lohkon lopussa
        rivit_.push_back(std::move(viesti));
    }

    std::size_t koko() const
    {
        std::scoped_lock lukko{mutex_};
        return rivit_.size();
    }

private:
    mutable std::mutex mutex_;
    std::vector<std::string> rivit_;
};
// @loppu mutex

int main()
{
    // @alku kaytto
    Loki loki;
    std::atomic<int> laskuri{0};
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < 4; ++s) {
            saikeet.emplace_back([&loki, &laskuri, s] {
                for (int i = 0; i < 1000; ++i) {
                    loki.kirjaa(std::format("säie {} rivi {}", s, i));
                    ++laskuri;   // atominen lisäys
                }
            });
        }
    }
    std::println("rivejä {}, laskuri {}", loki.koko(), laskuri.load());
    // @loppu kaytto
}
