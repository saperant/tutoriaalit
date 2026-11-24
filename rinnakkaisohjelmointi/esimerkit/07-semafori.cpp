// TSAN
// std::counting_semaphore rajoittaa samanaikaisia käyttäjiä,
// std::latch toimii lähtöporttina.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <latch>
#include <print>
#include <semaphore>
#include <thread>
#include <vector>

// @alku yhteydet
class Yhteysraja {
public:
    // Ottaa paikan; RAII-olio palauttaa sen.
    class Paikka {
    public:
        explicit Paikka(Yhteysraja& r) : raja_{r}
        {
            raja_.paikat_.acquire();
            const int nyt = ++raja_.kaytossa_;
            int vanha = raja_.suurin_.load();
            while (vanha < nyt &&
                   !raja_.suurin_.compare_exchange_weak(vanha, nyt)) {
            }
        }
        ~Paikka()
        {
            --raja_.kaytossa_;
            raja_.paikat_.release();
        }
        Paikka(const Paikka&) = delete;
        Paikka& operator=(const Paikka&) = delete;

    private:
        Yhteysraja& raja_;
    };

    int suurin() const { return suurin_.load(); }

private:
    std::counting_semaphore<3> paikat_{3};   // enintään 3 yhtä aikaa
    std::atomic<int> kaytossa_{0};
    std::atomic<int> suurin_{0};
};
// @loppu yhteydet

int main()
{
    using namespace std::chrono_literals;
    // @alku kaytto
    Yhteysraja raja;
    std::latch lahto{1};               // portti: avataan kerran
    std::atomic<int> pyyntoja{0};
    {
        std::vector<std::jthread> asiakkaat;
        for (int s = 0; s < 8; ++s) {
            asiakkaat.emplace_back([&] {
                lahto.wait();          // kaikki lähtevät yhtä aikaa
                for (int i = 0; i < 5; ++i) {
                    Yhteysraja::Paikka paikka{raja};
                    std::this_thread::sleep_for(1ms);  // "pyyntö"
                    ++pyyntoja;
                }
            });
        }
        lahto.count_down();
    }
    std::println("pyyntoja {}, samanaikaisia enintaan 3: {}",
                 pyyntoja.load(), raja.suurin() <= 3 ? "kylla" : "ei");
    // @loppu kaytto
}
