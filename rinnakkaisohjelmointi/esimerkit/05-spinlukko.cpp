// TSAN
// Spinlukko atomic_flagilla: test_and_set (acquire) ja clear (release).
// C++20:n wait/notify estää turhan pyörimisen pitkässä odotuksessa.
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
        while (lippu_.test_and_set(std::memory_order_acquire)) {
            // Odota, kunnes lippu näyttää vapaalta, ja yritä uudelleen.
            // wait(true) nukkuu, kun arvo on true (käyttöjärjestelmän
            // futex Linuxissa), eikä kuormita välimuistiväylää.
            lippu_.wait(true, std::memory_order_relaxed);
        }
    }

    void unlock() noexcept
    {
        lippu_.clear(std::memory_order_release);
        lippu_.notify_one();
    }

private:
    std::atomic_flag lippu_;   // C++20: alustuu tilaan false
};
// @loppu spinlukko

int main()
{
    // @alku kaytto
    Spinlukko lukko;
    long saldo = 0;                 // suojattu lukolla
    {
        std::vector<std::jthread> saikeet;
        for (int s = 0; s < 4; ++s) {
            saikeet.emplace_back([&] {
                for (int i = 0; i < 20'000; ++i) {
                    std::scoped_lock l{lukko};   // BasicLockable riittää
                    saldo += 3;
                    saldo -= 2;
                }
            });
        }
    }
    std::println("saldo: {}", saldo);
    // @loppu kaytto
}
