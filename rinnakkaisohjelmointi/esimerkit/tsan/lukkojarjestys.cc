// Lukkojärjestysvirhe: säie 1 ottaa lukot järjestyksessä A, B ja säie 2
// järjestyksessä B, A. Säikeet ajetaan peräkkäin, joten ohjelma ei
// tässä ajossa lukkiudu, mutta ThreadSanitizer huomaa, että se voisi.
#include <mutex>
#include <print>
#include <thread>

// @alku lukkojarjestys
std::mutex tilit;
std::mutex loki;

void siirto()                        // A, sitten B
{
    std::scoped_lock a{tilit};
    std::scoped_lock b{loki};
}

void raportti()                      // B, sitten A
{
    std::scoped_lock b{loki};
    std::scoped_lock a{tilit};
}

int main()
{
    std::jthread{siirto}.join();
    std::jthread{raportti}.join();
    std::println("ei lukkiutunut tassa ajossa");
}
// @loppu lukkojarjestys
