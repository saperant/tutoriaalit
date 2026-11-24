// TSAN
// Rajattu lukoton MPMC-jono (Dmitry Vjukovin rakenne): jokaisella
// paikalla on järjestysnumero, joka kertoo, kenen vuoro paikkaan on.
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <new>
#include <optional>
#include <print>
#include <thread>
#include <vector>

// @alku jono
template <class T, std::size_t N>
class MpmcJono {
    static_assert((N & (N - 1)) == 0, "N:n oltava kahden potenssi");

public:
    MpmcJono()
    {
        for (std::size_t i = 0; i < N; ++i) {
            paikat_[i].jarjestys.store(i, std::memory_order_relaxed);
        }
    }

    bool laita(const T& arvo)
    {
        std::size_t pos = kirjoitus_.load(std::memory_order_relaxed);
        for (;;) {
            Paikka& p = paikat_[pos & (N - 1)];
            const std::size_t j = p.jarjestys.load(std::memory_order_acquire);
            const auto ero = static_cast<std::ptrdiff_t>(j - pos);
            if (ero == 0) {               // paikka vapaa tälle kierrokselle
                if (kirjoitus_.compare_exchange_weak(
                        pos, pos + 1, std::memory_order_relaxed)) {
                    p.arvo = arvo;
                    p.jarjestys.store(pos + 1, std::memory_order_release);
                    return true;
                }                         // CAS päivitti pos:n
            } else if (ero < 0) {
                return false;             // täynnä
            } else {
                pos = kirjoitus_.load(std::memory_order_relaxed);
            }
        }
    }

    std::optional<T> ota()
    {
        std::size_t pos = luku_.load(std::memory_order_relaxed);
        for (;;) {
            Paikka& p = paikat_[pos & (N - 1)];
            const std::size_t j = p.jarjestys.load(std::memory_order_acquire);
            const auto ero = static_cast<std::ptrdiff_t>(j - (pos + 1));
            if (ero == 0) {               // paikassa on arvo
                if (luku_.compare_exchange_weak(
                        pos, pos + 1, std::memory_order_relaxed)) {
                    T arvo = p.arvo;
                    // Seuraavan kierroksen kirjoittaja saa paikan.
                    p.jarjestys.store(pos + N, std::memory_order_release);
                    return arvo;
                }
            } else if (ero < 0) {
                return std::nullopt;      // tyhjä
            } else {
                pos = luku_.load(std::memory_order_relaxed);
            }
        }
    }

private:
    struct Paikka {
        std::atomic<std::size_t> jarjestys;
        T arvo;
    };
    static constexpr std::size_t rivi =
        std::hardware_destructive_interference_size;
    alignas(rivi) std::array<Paikka, N> paikat_;
    alignas(rivi) std::atomic<std::size_t> kirjoitus_{0};
    alignas(rivi) std::atomic<std::size_t> luku_{0};
};
// @loppu jono

int main()
{
    // @alku kaytto
    MpmcJono<std::uint64_t, 256> jono;
    constexpr std::uint64_t per_tuottaja = 50'000;
    std::atomic<std::uint64_t> summa{0};
    std::atomic<std::uint64_t> otettu{0};
    {
        std::vector<std::jthread> saikeet;
        for (int k = 0; k < 2; ++k) {
            saikeet.emplace_back([&] {
                while (otettu.load() < 3 * per_tuottaja) {
                    if (auto arvo = jono.ota()) {
                        summa.fetch_add(*arvo, std::memory_order_relaxed);
                        otettu.fetch_add(1);
                    } else {
                        std::this_thread::yield();
                    }
                }
            });
        }
        for (std::uint64_t t = 0; t < 3; ++t) {
            saikeet.emplace_back([&jono, t] {
                for (std::uint64_t i = 1; i <= per_tuottaja; ++i) {
                    while (!jono.laita(i + t * per_tuottaja)) {
                        std::this_thread::yield();
                    }
                }
            });
        }
    }
    const std::uint64_t n = 3 * per_tuottaja;
    std::println("otettu {}, summa {} (odotettu {})", otettu.load(),
                 summa.load(), n * (n + 1) / 2);
    // @loppu kaytto
}
