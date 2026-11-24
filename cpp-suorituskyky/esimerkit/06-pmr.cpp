// Polymorfiset muistiresurssit (std::pmr): varaukset pinopuskurista ja
// muistipoolista.
#include <array>
#include <cstddef>
#include <cstdio>
#include <map>
#include <memory_resource>
#include <string>
#include <string_view>
#include <vector>

#include "laskuri.hpp"
#include "mittari.hpp"

// @alku laskeva
// Oma muistiresurssi: laskee, montako kertaa pooli pyytää muistia
// ylävirran resurssilta, ja välittää pyynnöt eteenpäin.
class Laskeva : public std::pmr::memory_resource {
public:
    explicit Laskeva(std::pmr::memory_resource* ylavirta)
        : ylavirta_{ylavirta} {}
    std::size_t pyyntoja() const { return pyyntoja_; }

private:
    void* do_allocate(std::size_t koko, std::size_t tasaus) override
    {
        ++pyyntoja_;
        return ylavirta_->allocate(koko, tasaus);
    }
    void do_deallocate(void* p, std::size_t koko,
                       std::size_t tasaus) override
    {
        ylavirta_->deallocate(p, koko, tasaus);
    }
    bool do_is_equal(const memory_resource& muu) const noexcept override
    {
        return this == &muu;
    }

    std::pmr::memory_resource* ylavirta_;
    std::size_t pyyntoja_ = 0;
};
// @loppu laskeva

// @alku monotoninen
// Rivit jäsennetään pinossa olevaan puskuriin. Ylävirtana on
// null_memory_resource, joka heittää std::bad_alloc-poikkeuksen, jos
// puskuri loppuu: näin varmistetaan, ettei keosta varata mitään.
std::size_t jasenna_pmr(std::string_view teksti)
{
    std::array<std::byte, 16384> puskuri;
    std::pmr::monotonic_buffer_resource areena{
        puskuri.data(), puskuri.size(), std::pmr::null_memory_resource()};
    std::pmr::vector<std::pmr::string> kentat{&areena};
    std::size_t alku = 0;
    while (alku <= teksti.size()) {
        std::size_t loppu = teksti.find(';', alku);
        if (loppu == std::string_view::npos) {
            loppu = teksti.size();
        }
        kentat.emplace_back(teksti.substr(alku, loppu - alku));
        alku = loppu + 1;
    }
    return kentat.size();
}   // koko puskuri vapautuu kerralla, purkajat eivät vapauta yksitellen
// @loppu monotoninen

std::size_t jasenna(std::string_view teksti)
{
    std::vector<std::string> kentat;
    std::size_t alku = 0;
    while (alku <= teksti.size()) {
        std::size_t loppu = teksti.find(';', alku);
        if (loppu == std::string_view::npos) {
            loppu = teksti.size();
        }
        kentat.emplace_back(teksti.substr(alku, loppu - alku));
        alku = loppu + 1;
    }
    return kentat.size();
}

// @alku pooli
// Hakemisto, jonka solmut tulevat poolista. Pooli pyytää ylävirralta
// isoja lohkoja ja jakaa ne samankokoisiksi paloiksi.
template <typename Kartta>
void tayta(Kartta& k, int n)
{
    for (int i = 0; i < n; ++i) {
        k[i * 7919 % n] = i;
    }
    for (int i = 0; i < n; i += 2) {
        k.erase(i);
    }
}
// @loppu pooli

int main(int argc, char** argv)
{
    std::string rivi;
    for (int i = 0; i < 50; ++i) {
        rivi += "kentta-numero-" + std::to_string(i) + ";";
    }
    rivi += "viimeinen";
    if (mittari::lue_tila({argv, static_cast<std::size_t>(argc)}).mittaa) {
        std::printf("1000 rivin jasennys, 51 kenttaa rivilla\n");
        auto t1 = mittari::mittaa([&] {
            for (int i = 0; i < 1000; ++i) {
                mittari::pida(jasenna(rivi));
            }
        }, 21);
        auto t2 = mittari::mittaa([&] {
            for (int i = 0; i < 1000; ++i) {
                mittari::pida(jasenna_pmr(rivi));
            }
        }, 21);
        mittari::tulosta("std::vector<std::string>", t1);
        mittari::tulosta("pmr ja pinopuskuri", t2, t1.mediaani_ms);
        std::printf("std::map, 100000 lisaysta ja 50000 poistoa\n");
        auto t3 = mittari::mittaa([] {
            std::map<int, int> k;
            tayta(k, 100'000);
        }, 11);
        auto t4 = mittari::mittaa([] {
            std::pmr::unsynchronized_pool_resource pooli;
            std::pmr::map<int, int> k{&pooli};
            tayta(k, 100'000);
        }, 11);
        mittari::tulosta("oletusvaraaja", t3);
        mittari::tulosta("unsynchronized_pool", t4, t3.mediaani_ms);
        return 0;
    }
    // @alku testi
    {
        laskuri::Jakso j;
        std::size_t n = jasenna(rivi);
        std::printf("std::vector<std::string>: kenttia %zu, varauksia %zu\n",
                    n, j.varaukset());
    }
    {
        laskuri::Jakso j;
        std::size_t n = jasenna_pmr(rivi);
        std::printf("pmr ja pinopuskuri:       kenttia %zu, varauksia %zu\n",
                    n, j.varaukset());
    }
    {
        laskuri::Jakso j;
        std::map<int, int> k;
        tayta(k, 1000);
        std::printf("std::map:  alkioita %zu, varauksia %zu\n", k.size(),
                    j.varaukset());
    }
    {
        laskuri::Jakso j;
        Laskeva laskeva{std::pmr::new_delete_resource()};
        std::pmr::unsynchronized_pool_resource pooli{&laskeva};
        std::pmr::map<int, int> k{&pooli};
        tayta(k, 1000);
        std::printf("pmr::map:  alkioita %zu, varauksia %zu, "
                    "poolin pyyntoja %zu\n",
                    k.size(), j.varaukset(), laskeva.pyyntoja());
    }
    // @loppu testi
}
