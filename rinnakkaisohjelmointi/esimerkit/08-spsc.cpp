// TSAN
// Lukoton rengaspuskuri yhdelle tuottajalle ja yhdelle kuluttajalle
// (SPSC). Kumpikin indeksi on vain yhden säikeen kirjoittama.
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <new>
#include <optional>
#include <print>
#include <thread>

// @alku rengas
template <class T, std::size_t N>
class Rengas {
    static_assert((N & (N - 1)) == 0, "N:n oltava kahden potenssi");

public:
    bool laita(const T& arvo)            // vain tuottaja kutsuu
    {
        const std::size_t t = tail_.load(std::memory_order_relaxed);
        if (t - head_.load(std::memory_order_acquire) == N) {
            return false;                // täynnä
        }
        alkiot_[t & (N - 1)] = arvo;
        tail_.store(t + 1, std::memory_order_release);   // julkaisu
        return true;
    }

    std::optional<T> ota()               // vain kuluttaja kutsuu
    {
        const std::size_t h = head_.load(std::memory_order_relaxed);
        if (h == tail_.load(std::memory_order_acquire)) {
            return std::nullopt;         // tyhjä
        }
        T arvo = alkiot_[h & (N - 1)];
        head_.store(h + 1, std::memory_order_release);   // paikka vapaa
        return arvo;
    }

private:
    static constexpr std::size_t rivi =
        std::hardware_destructive_interference_size;
    alignas(rivi) std::atomic<std::size_t> head_{0};  // kuluttajan
    alignas(rivi) std::atomic<std::size_t> tail_{0};  // tuottajan
    alignas(rivi) std::array<T, N> alkiot_{};
};
// @loppu rengas

int main()
{
    // @alku kaytto
    Rengas<std::uint32_t, 1024> rengas;
    constexpr std::uint32_t maara = 200'000;
    std::uint64_t summa = 0;
    bool jarjestyksessa = true;
    {
        std::jthread kuluttaja{[&] {
            std::uint32_t odotettu = 1;
            while (odotettu <= maara) {
                if (auto arvo = rengas.ota()) {
                    jarjestyksessa = jarjestyksessa && *arvo == odotettu;
                    summa += *arvo;
                    ++odotettu;
                } else {
                    std::this_thread::yield();
                }
            }
        }};
        std::jthread tuottaja{[&] {
            for (std::uint32_t i = 1; i <= maara; ++i) {
                while (!rengas.laita(i)) {
                    std::this_thread::yield();
                }
            }
        }};
    }
    std::println("summa {}, jarjestys sailyi: {}", summa,
                 jarjestyksessa ? "kylla" : "ei");
    // @loppu kaytto
}
