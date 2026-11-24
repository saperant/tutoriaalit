// TSAN
// Lukija–kirjoittaja-lukko: monta lukijaa yhtä aikaa, kirjoittaja yksin.
#include <atomic>
#include <mutex>
#include <print>
#include <shared_mutex>
#include <string>
#include <thread>
#include <vector>

// @alku asetukset
class Asetukset {
public:
    struct Tila {
        int versio = 0;
        std::string palvelin = "a0";
        int portti = 8000;
    };

    Tila lue() const
    {
        std::shared_lock lukko{mutex_};   // jaettu: lukijat rinnakkain
        return tila_;
    }

    void paivita(int versio)
    {
        std::unique_lock lukko{mutex_};   // yksinomainen
        tila_.versio = versio;
        tila_.palvelin = "a" + std::to_string(versio);
        tila_.portti = 8000 + versio;
    }

private:
    mutable std::shared_mutex mutex_;
    Tila tila_;
};
// @loppu asetukset

int main()
{
    // @alku kaytto
    Asetukset asetukset;
    std::atomic<int> rikkinaisia{0};
    std::atomic<bool> valmis{false};
    {
        std::vector<std::jthread> lukijat;
        for (int s = 0; s < 3; ++s) {
            lukijat.emplace_back([&] {
                while (!valmis.load()) {
                    const auto t = asetukset.lue();
                    // Kenttien on aina kuuluttava samaan versioon.
                    if (t.palvelin != "a" + std::to_string(t.versio) ||
                        t.portti != 8000 + t.versio) {
                        ++rikkinaisia;
                    }
                }
            });
        }
        for (int v = 1; v <= 2'000; ++v) {
            asetukset.paivita(v);
        }
        valmis = true;
    }
    std::println("viimeinen versio {}, rikkinaisia lukuja {}",
                 asetukset.lue().versio, rikkinaisia.load());
    // @loppu kaytto
}
