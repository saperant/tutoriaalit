// TSAN
// Ensimmäinen rinnakkainen ohjelma: summa osissa, jokainen säie omaan
// paikkaansa, tulokset yhdistetään vasta kun säikeet ovat valmiita.
#include <cstddef>
#include <cstdint>
#include <numeric>
#include <print>
#include <thread>
#include <vector>

// @alku summa
std::uint64_t rinnakkainen_summa(const std::vector<std::uint32_t>& luvut,
                                 std::size_t saikeita)
{
    std::vector<std::uint64_t> osasummat(saikeita, 0);
    {
        std::vector<std::jthread> saikeet;
        const std::size_t pala = luvut.size() / saikeita;
        for (std::size_t s = 0; s < saikeita; ++s) {
            const std::size_t alku = s * pala;
            const std::size_t loppu =
                s + 1 == saikeita ? luvut.size() : alku + pala;
            saikeet.emplace_back([&luvut, &osasummat, s, alku, loppu] {
                std::uint64_t summa = 0;
                for (std::size_t i = alku; i < loppu; ++i) {
                    summa += luvut[i];
                }
                osasummat[s] = summa;     // vain tämä säie kirjoittaa
            });
        }
    }   // jthreadien hajottimet odottavat kaikki säikeet
    return std::accumulate(osasummat.begin(), osasummat.end(),
                           std::uint64_t{0});
}
// @loppu summa

int main()
{
    // @alku kaytto
    std::vector<std::uint32_t> luvut(1'000'003);
    std::iota(luvut.begin(), luvut.end(), 1u);
    const std::uint64_t n = luvut.size();
    for (std::size_t saikeita : {1u, 2u, 4u, 7u}) {
        std::println("{} saietta: {}", saikeita,
                     rinnakkainen_summa(luvut, saikeita));
    }
    std::println("kaava n(n+1)/2: {}", n * (n + 1) / 2);
    // @loppu kaytto
}
