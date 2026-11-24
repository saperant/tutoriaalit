// TSAN
// std::atomic_ref: tavallista taulukkoa käsitellään atomisesti
// rinnakkaisen vaiheen ajan ja tavallisena sen jälkeen.
#include <atomic>
#include <cstdint>
#include <print>
#include <thread>
#include <vector>

int main()
{
    // @alku histogrammi
    std::vector<std::uint32_t> data(400'000);
    for (std::size_t i = 0; i < data.size(); ++i) {
        data[i] = static_cast<std::uint32_t>(i * 2654435761u);  // sekoitus
    }
    std::vector<int> histogrammi(16, 0);   // tavallisia int-arvoja
    {
        std::vector<std::jthread> saikeet;
        const std::size_t pala = data.size() / 4;
        for (std::size_t s = 0; s < 4; ++s) {
            saikeet.emplace_back([&data, &histogrammi, s, pala] {
                for (std::size_t i = s * pala; i < (s + 1) * pala; ++i) {
                    const std::size_t lokero = data[i] >> 28;
                    std::atomic_ref<int> laskuri{histogrammi[lokero]};
                    laskuri.fetch_add(1, std::memory_order_relaxed);
                }
            });
        }
    }   // join: rinnakkainen vaihe on ohi, tavallinen luku on turvallinen
    int yhteensa = 0;
    for (std::size_t k = 0; k < histogrammi.size(); ++k) {
        std::print("{}{}", k == 0 ? "" : " ", histogrammi[k]);
        yhteensa += histogrammi[k];
    }
    std::println("\nyhteensa {}", yhteensa);
    // @loppu histogrammi
}
