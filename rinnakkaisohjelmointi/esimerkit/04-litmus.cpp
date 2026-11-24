// TSAN
// Litmus-testit: kaksi säiettä ajaa lyhyen ohjelman tuhansia kertoja, ja
// jokaisen kierroksen lopputulos (r1, r2) kirjataan. Muistimalli kertoo,
// mitkä lopputulokset ovat sallittuja; havaittujen on kuuluttava niihin.
// Havaintojen määrät tulostetaan virhetulosteeseen, koska ne riippuvat
// koneesta ja kuormasta.
#include <array>
#include <atomic>
#include <barrier>
#include <chrono>
#include <cstdio>
#include <format>
#include <print>
#include <set>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

using Tulos = std::pair<int, int>;

// @alku ajuri
// Ajaa enintään 'kierroksia' kierrosta, mutta lopettaa aikarajaan, jotta
// kuormitettu kone (tai ThreadSanitizer) ei venytä testiä.
template <class Saie1, class Saie2, class Nollaa>
std::array<int, 4> aja(int kierroksia, Saie1 s1, Saie2 s2, Nollaa nollaa)
{
    using Kello = std::chrono::steady_clock;
    const auto raja = Kello::now() + std::chrono::seconds{2};
    std::array<int, 4> maarat{};
    int r1 = 0;
    int r2 = 0;
    int vaihe = 0;
    bool jatka = true;
    // Valmistumisfunktio ajetaan, kun molemmat säikeet ovat saapuneet,
    // ja ennen kuin kumpikaan jatkaa: se näkee kierroksen tuloksen ja
    // päättää molempien puolesta, aloitetaanko uusi kierros.
    std::barrier este{2, [&]() noexcept {
        if (vaihe++ % 2 == 1) {
            ++maarat[static_cast<std::size_t>(r1 * 2 + r2)];
            nollaa();
        } else {
            jatka = vaihe / 2 < kierroksia && Kello::now() < raja;
        }
    }};
    auto silmukka = [&](auto&& runko) {
        for (;;) {
            este.arrive_and_wait();     // yhteinen lähtö
            if (!jatka) {
                return;
            }
            runko();
            este.arrive_and_wait();     // kierros valmis
        }
    };
    {
        std::jthread a{[&] { silmukka([&] { r1 = s1(); }); }};
        std::jthread b{[&] { silmukka([&] { r2 = s2(); }); }};
    }   // säikeet valmiita ennen kuin maarat palautetaan
    return maarat;
}
// @loppu ajuri

void raportoi(std::string_view nimi, const std::array<int, 4>& maarat,
              const std::set<Tulos>& sallitut)
{
    bool kaikki_sallittuja = true;
    std::string sallitut_teksti;
    for (int i = 0; i < 4; ++i) {
        const Tulos t{i / 2, i % 2};
        if (sallitut.contains(t)) {
            sallitut_teksti += std::format(" ({},{})", t.first, t.second);
        } else if (maarat[static_cast<std::size_t>(i)] > 0) {
            kaikki_sallittuja = false;
        }
        std::print(stderr, "{} ({},{}): {}\n", nimi, t.first, t.second,
                   maarat[static_cast<std::size_t>(i)]);
    }
    std::println("{}: sallitut{}; havainnot sallittuja: {}", nimi,
                 sallitut_teksti, kaikki_sallittuja ? "kylla" : "EI");
}

int main()
{
    constexpr int kierroksia = 20'000;
    std::atomic<int> x{0};
    std::atomic<int> y{0};
    auto nollaa = [&] {
        x.store(0, std::memory_order_relaxed);
        y.store(0, std::memory_order_relaxed);
    };
    using enum std::memory_order;

    // @alku sb
    // Store buffering: kumpikin kirjoittaa omaan ja lukee toisen.
    auto sb = [&](std::memory_order kirj, std::memory_order luku) {
        return aja(kierroksia,
            [&] { x.store(1, kirj); return y.load(luku); },
            [&] { y.store(1, kirj); return x.load(luku); }, nollaa);
    };
    raportoi("SB relaxed", sb(relaxed, relaxed),
             {{0, 0}, {0, 1}, {1, 0}, {1, 1}});
    raportoi("SB release/acquire", sb(release, acquire),
             {{0, 0}, {0, 1}, {1, 0}, {1, 1}});
    raportoi("SB seq_cst", sb(seq_cst, seq_cst),
             {{0, 1}, {1, 0}, {1, 1}});
    // @loppu sb

    // @alku mp
    // Message passing: x on data, y lippu. Toinen säie lukee lipun
    // (r1) ja sitten datan (r2).
    auto mp = [&](std::memory_order kirj, std::memory_order luku) {
        return aja(kierroksia,
            [&] { x.store(1, relaxed); y.store(1, kirj); return 0; },
            [&] {
                const int lippu = y.load(luku);
                return lippu * 2 + x.load(relaxed);
            }, nollaa);
    };
    // @loppu mp
    // Ensimmäinen säie palauttaa 0, joten tulos (r1, r2) on
    // (lippu, data) koodattuna toisen säikeen paluuarvoon.
    raportoi("MP relaxed", mp(relaxed, relaxed),
             {{0, 0}, {0, 1}, {1, 0}, {1, 1}});
    raportoi("MP release/acquire", mp(release, acquire),
             {{0, 0}, {0, 1}, {1, 1}});
}
