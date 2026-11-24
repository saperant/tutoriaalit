// Julkaisu relaxed-lipulla: lippu on atominen, mutta data ei. Ilman
// release/acquire-paria datan kirjoitus ja luku eivät ole järjestyksessä,
// joten ThreadSanitizer raportoi kilpailun datasta.
#include <atomic>
#include <print>
#include <thread>

// @alku julkaisu
int data = 0;
std::atomic<bool> valmis{false};

int main()
{
    std::jthread kirjoittaja{[] {
        data = 42;
        valmis.store(true, std::memory_order_relaxed);   // VIRHE
    }};
    std::jthread lukija{[] {
        while (!valmis.load(std::memory_order_relaxed)) {
            std::this_thread::yield();
        }
        const int luettu = data;
        std::println("data {}", luettu);
    }};
}
// @loppu julkaisu
