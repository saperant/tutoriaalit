// TSAN
#include <cstddef>
#include <numeric>
#include <print>
#include <thread>
#include <vector>

int main()
{
    // @alku jthread
    std::vector<long long> luvut(1'000'000);
    std::iota(luvut.begin(), luvut.end(), 1);

    constexpr std::size_t saikeita = 4;
    std::vector<long long> osasummat(saikeita);   // oma paikka kullekin
    const std::size_t pala = luvut.size() / saikeita;
    {
        std::vector<std::jthread> tyontekijat;
        for (std::size_t i = 0; i < saikeita; ++i) {
            tyontekijat.emplace_back([&luvut, &osasummat, pala, i] {
                auto alku = luvut.begin() + i * pala;
                auto loppu = (i + 1 == saikeita) ? luvut.end()
                                                 : alku + pala;
                osasummat[i] = std::accumulate(alku, loppu, 0LL);
            });
        }
    }   // jthread-oliot odottavat säikeiden päättymistä tässä

    auto summa = std::accumulate(osasummat.begin(), osasummat.end(), 0LL);
    std::println("summa: {}", summa);
    // @loppu jthread
}
