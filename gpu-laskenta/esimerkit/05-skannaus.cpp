// Prefiksisumma: Hillis–Steele ja Blelloch lohkossa, monitasoinen
// skannaus miljoonalle alkiolle ja sen käyttö virran tiivistykseen.
#include "data.hpp"
#include "skannaus.hpp"

#include <algorithm>
#include <numeric>
#include <vector>

// @alku tyomaara
// Algoritmit CPU:lla askel kerrallaan samassa järjestyksessä kuin
// varjostimissa, yhteenlaskut ja tahdistuskierrokset laskettuina.
struct Tyo {
    std::size_t lisayksia = 0, kierroksia = 0;
};

Tyo hillis_steele(std::vector<std::uint32_t>& t) {
    Tyo tyo;
    for (std::size_t d = 1; d < t.size(); d *= 2, ++tyo.kierroksia) {
        const auto vanha = t;
        for (std::size_t i = d; i < t.size(); ++i, ++tyo.lisayksia) {
            t[i] = vanha[i] + vanha[i - d];
        }
    }
    return tyo;
}

Tyo blelloch(std::vector<std::uint32_t>& t) {
    Tyo tyo;
    const std::size_t n = t.size();
    for (std::size_t vali = 1; vali < n; vali *= 2, ++tyo.kierroksia) {
        for (std::size_t i = 2 * vali - 1; i < n; i += 2 * vali) {
            t[i] += t[i - vali];
            ++tyo.lisayksia;
        }
    }
    t[n - 1] = 0;
    for (std::size_t vali = n / 2; vali >= 1; vali /= 2) {
        for (std::size_t i = 2 * vali - 1; i < n; i += 2 * vali) {
            const std::uint32_t v = t[i - vali];
            t[i - vali] = t[i];
            t[i] += v;
            ++tyo.lisayksia;
        }
        ++tyo.kierroksia;
    }
    return tyo;
}
// @loppu tyomaara

struct Ehto {
    std::uint32_t n, jakaja;
};

int main() {
    Satunnainen s(5);
    // Työmäärä 512 alkion lohkolle.
    {
        std::vector<std::uint32_t> a(512), b(512), odotettu(512);
        std::ranges::generate(a, [&] { return s.u32() % 10; });
        b = a;
        std::exclusive_scan(a.begin(), a.end(), odotettu.begin(), 0u);
        auto kattava = odotettu;
        for (std::size_t i = 0; i < a.size(); ++i) kattava[i] += a[i];
        const Tyo hs = hillis_steele(a);
        const Tyo bl = blelloch(b);
        std::println("512 alkion lohko    lisayksia  kierroksia  oikein");
        std::println("Hillis-Steele       {:9}  {:10}  {}", hs.lisayksia,
                     hs.kierroksia, kylla(a == kattava));
        std::println("Blelloch            {:9}  {:10}  {}", bl.lisayksia,
                     bl.kierroksia, kylla(b == odotettu));
    }

    VkYmparisto vk;
    // Hillis–Steele GPU:lla lohkoittain (kattava summa 256 alkiolle).
    {
        Puskuri<std::uint32_t> data(vk, 256 * 64);
        std::ranges::generate(data.alkiot(), [&] { return s.u32() % 10; });
        std::vector<std::uint32_t> odotettu(data.koko());
        for (std::ptrdiff_t alku = 0; alku < 256 * 64; alku += 256) {
            std::inclusive_scan(data.alkiot().begin() + alku,
                                data.alkiot().begin() + alku + 256,
                                odotettu.begin() + alku);
        }
        Putki hs(vk, "bin/skannaus_hs.spv", 1);
        VkCommandBuffer kp = vk.aloita();
        hs.aja(kp, hs.joukko({data.puskuri}), {64});
        vk.suorita(kp);
        std::println("\nHillis-Steele GPU:lla, 64 lohkoa: oikein {}",
                     kylla(eroavia<std::uint32_t>(data.alkiot(),
                                                  odotettu) == 0));
    }

    // @alku suuri
    constexpr std::uint32_t n = 1'000'000;
    Puskuri<std::uint32_t> x(vk, n), paikat(vk, n), kohde(vk, n);
    std::ranges::generate(x.alkiot(), [&] { return s.u32() % 1000; });
    Putki liputa(vk, "bin/liputa.spv", 2, sizeof(Ehto));
    Putki tiivista(vk, "bin/tiivista.spv", 3, sizeof(Ehto));
    Skannaus skannaus(vk, paikat);
    const Ehto ehto{n, 3};

    VkCommandBuffer kp = vk.aloita();
    liputa.aja(kp, liputa.joukko({x.puskuri, paikat.puskuri}), ehto,
               {ryhmia(n, 256)});
    laskentaeste(kp);
    const int ajoja = skannaus.tallenna(kp);
    tiivista.aja(kp, tiivista.joukko({x.puskuri, paikat.puskuri,
                                      kohde.puskuri}),
                 ehto, {ryhmia(n, 256)});
    vk.suorita(kp);
    // @loppu suuri

    std::vector<std::uint32_t> liput(n), odotetut_paikat(n);
    std::ranges::transform(x.alkiot(), liput.begin(), [](std::uint32_t v) {
        return v % 3 == 0 ? 1u : 0u;
    });
    std::exclusive_scan(liput.begin(), liput.end(),
                        odotetut_paikat.begin(), 0u);
    std::vector<std::uint32_t> valitut;
    std::ranges::copy_if(x.alkiot(), std::back_inserter(valitut),
                         [](std::uint32_t v) { return v % 3 == 0; });
    const std::uint32_t maara = paikat.alkiot()[n - 1] + liput[n - 1];
    std::println("\nmonitasoinen skannaus, {} alkiota:", n);
    std::println("tasoja {}, skannauksen ajoja {}", skannaus.tasoja(),
                 ajoja);
    std::println("paikat oikein: {}",
                 kylla(eroavia<std::uint32_t>(paikat.alkiot(),
                                              odotetut_paikat) == 0));
    std::println("tiivistys: {} alkiota jaollisia 3:lla, oikein: {}",
                 maara,
                 kylla(maara == valitut.size() &&
                       std::ranges::equal(kohde.alkiot().first(maara),
                                          valitut)));
    return Validointi::raportti();
}
