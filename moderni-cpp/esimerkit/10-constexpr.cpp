#include <array>
#include <cstddef>
#include <numeric>
#include <print>
#include <vector>

// @alku funktio
constexpr long long kertoma(int n)
{
    long long tulos = 1;
    for (int i = 2; i <= n; ++i) {
        tulos *= i;
    }
    return tulos;
}

static_assert(kertoma(5) == 120);
static_assert(kertoma(20) == 2'432'902'008'176'640'000);
// @loppu funktio

// @alku taulukko
constexpr std::array<int, 10> neliot = [] {
    std::array<int, 10> t{};
    for (std::size_t i = 0; i < t.size(); ++i) {
        t[i] = static_cast<int>(i * i);
    }
    return t;
}();

static_assert(neliot[9] == 81);
// @loppu taulukko

// @alku vektori
constexpr int alkulukujen_summa(int raja)
{
    std::vector<bool> alkuluku(raja + 1, true);   // C++20: sallittu
    int summa = 0;
    for (int i = 2; i <= raja; ++i) {
        if (alkuluku[i]) {
            summa += i;
            for (int j = i * i; j <= raja; j += i) {
                alkuluku[j] = false;
            }
        }
    }
    return summa;
}

static_assert(alkulukujen_summa(10) == 2 + 3 + 5 + 7);
// @loppu vektori

// @alku consteval
consteval int kilotavuja(int n)
{
    return n * 1024;
}

constinit int puskurin_koko = kilotavuja(4);
// @loppu consteval

int main()
{
    // @alku kaytto
    constexpr auto k10 = kertoma(10);   // laskettu käännösaikana
    int n = 15;
    auto k15 = kertoma(n);              // laskettu ajoaikana
    std::println("{} {}", k10, k15);

    std::println("{}", std::accumulate(neliot.begin(), neliot.end(), 0));
    std::println("{}", alkulukujen_summa(100));
    std::println("{}", puskurin_koko);
    // @loppu kaytto
}
