// TSAN
// Julkaisu release/acquire-parilla: tavallinen data kirjoitetaan
// ennen lipun release-kirjoitusta ja luetaan acquire-lukemisen jälkeen.
#include <atomic>
#include <print>
#include <string>
#include <thread>
#include <vector>

// @alku julkaisu
struct Asetukset {
    std::string nimi;
    std::vector<int> portit;
};

Asetukset asetukset;                  // ei atominen
std::atomic<bool> valmis{false};

void julkaise()
{
    asetukset.nimi = "palvelin";      // (1) tavalliset kirjoitukset
    asetukset.portit = {80, 443};
    valmis.store(true, std::memory_order_release);   // (2)
}

void lue()
{
    while (!valmis.load(std::memory_order_acquire)) {  // (3)
        std::this_thread::yield();
    }
    // (2) synkronoituu (3):n kanssa, joten (1) tapahtuu ennen tätä.
    std::println("{}: {} porttia, ensimmainen {}", asetukset.nimi,
                 asetukset.portit.size(), asetukset.portit.front());
}
// @loppu julkaisu

int main()
{
    std::jthread lukija{lue};
    std::jthread kirjoittaja{julkaise};
}
