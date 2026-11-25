// Kantalukulajittelu (LSD radix sort) GPU:lla: 4 bittiä kierroksella,
// ja jokainen kierros on laskenta, prefiksisumma ja hajautus. Lopuksi
// tarkistetaan vakaus lajittelemalla vain avainten yläbittien mukaan.
#include "data.hpp"
#include "skannaus.hpp"

#include <algorithm>
#include <vector>

struct Vakiot {
    std::uint32_t n, siirto, ryhmia;
};

// @alku lajittelija
class Kantalukulajittelu {
public:
    Kantalukulajittelu(const VkYmparisto& vk, Puskuri<std::uint32_t>& a,
                       Puskuri<std::uint32_t>& b)
        : n_{static_cast<std::uint32_t>(a.koko())},
          ryhmia_{ryhmia(n_, 256)}, laskut_(vk, 16 * ryhmia_),
          laske_(vk, "bin/radix_laske.spv", 2, sizeof(Vakiot)),
          hajota_(vk, "bin/radix_hajota.spv", 3, sizeof(Vakiot)),
          skannaus_(vk, laskut_) {
        laske_a_ = laske_.joukko({a.puskuri, laskut_.puskuri});
        laske_b_ = laske_.joukko({b.puskuri, laskut_.puskuri});
        a_b_ = hajota_.joukko({a.puskuri, laskut_.puskuri, b.puskuri});
        b_a_ = hajota_.joukko({b.puskuri, laskut_.puskuri, a.puskuri});
    }

    // Lajittelee bittien [alkubitti, 32) mukaan. Kierroksia on parillinen
    // määrä, joten tulos päätyy takaisin puskuriin a.
    int tallenna(VkCommandBuffer kp, std::uint32_t alkubitti) const {
        int ajoja = 0;
        bool a_lahteena = true;
        for (std::uint32_t siirto = alkubitti; siirto < 32; siirto += 4) {
            const Vakiot v{n_, siirto, ryhmia_};
            laske_.aja(kp, a_lahteena ? laske_a_ : laske_b_, v, {ryhmia_});
            laskentaeste(kp);
            ajoja += 1 + skannaus_.tallenna(kp);
            hajota_.aja(kp, a_lahteena ? a_b_ : b_a_, v, {ryhmia_});
            laskentaeste(kp);
            ajoja += 1;
            a_lahteena = !a_lahteena;
        }
        return ajoja;
    }

private:
    std::uint32_t n_, ryhmia_;
    Puskuri<std::uint32_t> laskut_;
    Putki laske_, hajota_;
    Skannaus skannaus_;
    VkDescriptorSet laske_a_, laske_b_, a_b_, b_a_;
};
// @loppu lajittelija

int main(int argc, char** argv) {
    const bool mittaa = mittaustila(argc, argv);
    VkYmparisto vk;
    Satunnainen s(8);
    Ajastin ajastin(vk, 2);
    {
        constexpr std::uint32_t n = 1'000'000;
        Puskuri<std::uint32_t> a(vk, n), b(vk, n);
        std::ranges::generate(a.alkiot(), [&] { return s.u32(); });
        std::vector<std::uint32_t> odotettu(a.alkiot().begin(),
                                            a.alkiot().end());
        std::ranges::sort(odotettu);
        Kantalukulajittelu lajittelu(vk, a, b);
        VkCommandBuffer kp = vk.aloita();
        ajastin.merkitse(kp, 0);
        const int ajoja = lajittelu.tallenna(kp, 0);
        ajastin.merkitse(kp, 1);
        vk.suorita(kp);
        std::println("{} satunnaista 32-bittista avainta, 8 kierrosta, "
                     "{} ajoa", n, ajoja);
        std::println("sama kuin std::sort: {}",
                     kylla(std::ranges::equal(a.alkiot(), odotettu)));
        if (mittaa) {
            std::println("    aika {:.2f} ms", ajastin.lue()[0] / 1e6);
        }
    }
    // @alku vakaus
    // Vakaus: yläbitit ovat avain ja alabitit alkuperäinen järjestys.
    // Lajitellaan vain yläbittien mukaan (4 kierrosta), jolloin saman
    // avaimen alkioiden on säilytettävä keskinäinen järjestyksensä.
    {
        constexpr std::uint32_t n = 65'536;
        Puskuri<std::uint32_t> a(vk, n), b(vk, n);
        for (std::uint32_t i = 0; i < n; ++i) {
            a.alkiot()[i] = (s.u32() % 1000) << 16 | i;
        }
        std::vector<std::uint32_t> odotettu(a.alkiot().begin(),
                                            a.alkiot().end());
        std::ranges::stable_sort(odotettu, {}, [](std::uint32_t v) {
            return v >> 16;
        });
        Kantalukulajittelu lajittelu(vk, a, b);
        VkCommandBuffer kp = vk.aloita();
        lajittelu.tallenna(kp, 16);
        vk.suorita(kp);
        std::println("vakaus, {} avainta, 4 kierrosta: sama kuin "
                     "std::stable_sort: {}", n,
                     kylla(std::ranges::equal(a.alkiot(), odotettu)));
    }
    // @loppu vakaus
    return Validointi::raportti();
}
