// Litmus-testit tiukalla tahdistuksella: säikeet on sidottu eri ytimiin,
// ja ne odottavat pyörimällä yhteistä lähtöhetkeä, joka annetaan
// suorittimen aikaleimalaskurin (TSC) arvona. Näin ne lähtevät
// liikkeelle muutaman jakson sisällä toisistaan, ja laitteiston
// sallimat harvinaiset lopputulokset tulevat näkyviin. Tämä on
// mittausohjelma: havaintojen määrät riippuvat koneesta, joten se ajetaan
// käsin (make tulokset) eikä kuulu testeihin.
#include <array>
#include <atomic>
#include <cstdio>
#include <print>
#include <string_view>
#include <thread>

#include <pthread.h>
#include <sched.h>
#if defined(__x86_64__)
#include <x86intrin.h>
#endif

namespace {

void sido_ytimeen(int ydin)
{
    cpu_set_t joukko;
    CPU_ZERO(&joukko);
    CPU_SET(ydin, &joukko);
    // Sidonta voi epäonnistua kontissa; silloin mitataan ilman sitä.
    (void)pthread_setaffinity_np(pthread_self(), sizeof joukko, &joukko);
}

// Aikaleimalaskuri on kaikilla ytimillä sama kello. Muilla
// arkkitehtuureilla lähtöhetkeä ei käytetä.
inline unsigned long long tsc()
{
#if defined(__x86_64__)
    return __rdtsc();
#else
    return ~0ULL;
#endif
}

// @alku ajuri
// Pääsäie julkaisee kierroksen numeron ja lähtöhetken; työsäikeet
// pyörivät, kunnes hetki koittaa, ajavat runkonsa ja kuittaavat.
// Mikään säie ei nuku.
template <class Saie1, class Saie2, class Nollaa, class Esilue>
std::array<long, 4> aja(long kierroksia, Saie1 s1, Saie2 s2, Nollaa nollaa,
                        Esilue esilue)
{
    std::atomic<long> kierros{0};
    std::atomic<unsigned long long> lahto{0};
    std::atomic<int> valmiita{0};
    int r1 = 0;
    int r2 = 0;
    auto tyo = [&](int ydin, auto&& runko, int& tulos) {
        sido_ytimeen(ydin);
        for (long k = 1; k <= kierroksia; ++k) {
            while (kierros.load(std::memory_order_acquire) != k) {
            }
            esilue();   // rivit jaettuun tilaan tämän ytimen välimuistiin
            const auto hetki = lahto.load(std::memory_order_relaxed);
            while (tsc() < hetki) {
            }
            tulos = runko();
            valmiita.fetch_add(1, std::memory_order_release);
        }
    };
    std::array<long, 4> maarat{};
    {
        std::jthread a{[&] { tyo(1, s1, r1); }};
        std::jthread b{[&] { tyo(2, s2, r2); }};
        sido_ytimeen(0);
        for (long k = 1; k <= kierroksia; ++k) {
            nollaa();
            valmiita.store(0, std::memory_order_relaxed);
            lahto.store(tsc() + 4000, std::memory_order_relaxed);
            kierros.store(k, std::memory_order_release);
            while (valmiita.load(std::memory_order_acquire) != 2) {
            }
            ++maarat[static_cast<std::size_t>(r1 * 2 + r2)];
        }
    }
    return maarat;
}
// @loppu ajuri

void raportoi(std::string_view nimi, const std::array<long, 4>& m)
{
    std::println("{:<20}{:>9}{:>9}{:>9}{:>9}", nimi, m[0], m[1], m[2], m[3]);
}

// Muuttujat eri välimuistiriveille: kirjoitus viipyy puskurissa niin
// kauan kuin rivin omistuksen hakeminen toiselta ytimeltä kestää.
alignas(64) std::atomic<int> x{0};
alignas(64) std::atomic<int> y{0};

constexpr long kierroksia = 1'000'000;

void nollaa()
{
    x.store(0, std::memory_order_relaxed);
    y.store(0, std::memory_order_relaxed);
}

// Kumpikin säie lukee molemmat muuttujat ennen lähtöä. Silloin luku
// osuu omaan välimuistiin, mutta kirjoitus joutuu ensin mitätöimään
// toisen ytimen kopion ja odottaa sen ajan kirjoituspuskurissa.
void esilue()
{
    const int v = x.load(std::memory_order_relaxed)
                + y.load(std::memory_order_relaxed);
#if defined(__x86_64__)
    asm volatile("" : : "r"(v));    // estää latausten poistamisen
#else
    (void)v;
#endif
}

// @alku testit
// Järjestys on mallin parametri eli käännösaikainen vakio. Jos se
// annettaisiin ajonaikaisena arvona, GCC kääntäisi jokaisen
// kirjoituksen varmuuden vuoksi seq_cst-muotoon (xchg), eikä heikompaa
// järjestystä mitattaisi lainkaan.
template <std::memory_order kirj, std::memory_order luku>
std::array<long, 4> sb()
{
    return aja(kierroksia,
        [] { x.store(1, kirj); return y.load(luku); },
        [] { y.store(1, kirj); return x.load(luku); }, nollaa, esilue);
}

// MP: toinen säie palauttaa lipun ja datan koodattuna (lippu*2+data).
template <std::memory_order kirj, std::memory_order luku>
std::array<long, 4> mp()
{
    using enum std::memory_order;
    return aja(kierroksia,
        [] { x.store(1, relaxed); y.store(1, kirj); return 0; },
        [] {
            const int lippu = y.load(luku);
            return lippu * 2 + x.load(relaxed);
        }, nollaa, esilue);
}
// @loppu testit

}  // namespace

int main()
{
    using enum std::memory_order;
    std::println("litmus-testit, {} kierrosta, {} ydinta", kierroksia,
                 std::thread::hardware_concurrency());
    std::println("{:<20}{:>9}{:>9}{:>9}{:>9}", "(r1,r2)", "(0,0)", "(0,1)",
                 "(1,0)", "(1,1)");
    raportoi("SB relaxed", sb<relaxed, relaxed>());
    raportoi("SB release/acquire", sb<release, acquire>());
    raportoi("SB seq_cst", sb<seq_cst, seq_cst>());
    raportoi("MP relaxed", mp<relaxed, relaxed>());
    raportoi("MP release/acquire", mp<release, acquire>());
}
