// TSAN
// Kaksi lukkoa atomic_flagilla: spinlukko, joka odottaa pyörimällä, ja
// odottava lukko, joka nukkuu C++20:n wait/notify-parilla.
#include <atomic>
#include <mutex>
#include <print>
#include <thread>
#include <vector>

// @alku spinlukko
class Spinlukko {
public:
    void lock() noexcept
    {
        // test_and_set asettaa lipun ja palauttaa vanhan arvon: false
        // tarkoittaa, että lukko oli vapaa ja on nyt meidän.
        while (lippu_.test_and_set(std::memory_order_acquire)) {
            // Pyöri lukemalla, kunnes lippu näyttää vapaalta. Pelkkä
            // luku ei vie välimuistiriviä muilta säikeiltä, toisin
            // kuin toistuva test_and_set.
            while (lippu_.test(std::memory_order_relaxed)) {
            }
        }
    }

    void unlock() noexcept { lippu_.clear(std::memory_order_release); }

private:
    std::atomic_flag lippu_;   // C++20: alustuu tilaan false
};
// @loppu spinlukko

// @alku odottava
class OdottavaLukko {
public:
    void lock() noexcept
    {
        while (lippu_.test_and_set(std::memory_order_acquire)) {
            // wait(true) nukkuu niin kauan kuin arvo on true (Linuxissa
            // futex), eikä odottaja kuluta suoritinta.
            lippu_.wait(true, std::memory_order_relaxed);
        }
    }

    void unlock() noexcept
    {
        lippu_.clear(std::memory_order_release);
        lippu_.notify_one();
    }

private:
    std::atomic_flag lippu_;
};
// @loppu odottava

// @alku kaytto
template <typename Lukko>
long kokeile(int saikeita)
{
    Lukko lukko;
    long saldo = 0;                 // suojattu lukolla
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < saikeita; ++s) {
            saikeet.emplace_back([&] {
                for (int i = 0; i < 20'000; ++i) {
                    std::scoped_lock l{lukko};   // BasicLockable riittää
                    saldo += 3;
                    saldo -= 2;
                }
            });
        }
    }
    return saldo;
}

int main()
{
    // Spinlukolle enintään niin monta säiettä kuin ytimiä; muuten
    // lukon haltija voi vuorontua pois ja muut pyörivät turhaan.
    std::println("spinlukko, 2 säiettä: saldo {}", kokeile<Spinlukko>(2));
    std::println("odottava lukko, 4 säiettä: saldo {}",
                 kokeile<OdottavaLukko>(4));
}
// @loppu kaytto
