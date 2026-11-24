// TSAN
// Poolin sisäinen odotus: tehtävä, joka odottaa saman poolin
// alitehtävää, voi jumittaa koko poolin.
#include <chrono>
#include <future>
#include <print>

#include "yhteinen/saiepooli.hpp"

int main()
{
    using namespace std::chrono_literals;
    // @alku jumi
    Saiepooli pooli{1};       // yksi työntekijä tekee ongelman varmaksi
    auto ulompi = pooli.laheta([&pooli] {
        auto sisempi = pooli.laheta([] { return 21; });
        // Ainoa työntekijä on tässä odottamassa, joten sisempi tehtävä
        // ei voi alkaa. Ilman aikarajaa odotus ei päättyisi koskaan.
        if (sisempi.wait_for(200ms) == std::future_status::timeout) {
            return -1;
        }
        return 2 * sisempi.get();
    });
    std::println("ulompi tehtava: {}", ulompi.get());
    // @loppu jumi

    // @alku ratkaisu
    // Ratkaisu: ulompi tehtävä ei odota, vaan jatko lähetetään
    // alitehtävän perään (jatkokutsutyyli).
    std::promise<int> lopputulos;
    auto valmis = lopputulos.get_future();
    (void)pooli.laheta([&pooli, &lopputulos] {
        (void)pooli.laheta([&lopputulos] {
            const int osa = 21;
            lopputulos.set_value(2 * osa);   // jatko tässä
        });
    });
    std::println("jatkokutsuna: {}", valmis.get());
    // @loppu ratkaisu
}
