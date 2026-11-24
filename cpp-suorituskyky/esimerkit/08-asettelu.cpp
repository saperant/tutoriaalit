// Olioiden koko: täyte, tasaus, tyhjät jäsenet ja std::vector<bool>.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <functional>
#include <optional>
#include <variant>
#include <vector>

// @alku tayte
// Jäsenet ovat muistissa esittelyjärjestyksessä, ja jokainen tasataan
// omaan tasaukseensa. Väärä järjestys jättää rakenteeseen aukkoja.
struct Huono {
    bool aktiivinen;      // 1 + 7 täytettä
    double saldo;         // 8
    bool suljettu;        // 1 + 3 täytettä
    std::int32_t tunnus;  // 4
    bool lukittu;         // 1 + 7 täytettä lopussa
};

struct Hyva {
    double saldo;
    std::int32_t tunnus;
    bool aktiivinen;
    bool suljettu;
    bool lukittu;         // 1 täyte lopussa
};

static_assert(sizeof(Huono) == 32);
static_assert(sizeof(Hyva) == 16);
// @loppu tayte

// @alku tyhja
// Tyhjä vertailija vie jäsenenä tavun ja tasauksen verran tilaa, ellei
// sitä merkitä [[no_unique_address]]-määreellä.
template <typename Vertaa>
struct Rajat {
    int pienin, suurin;
    Vertaa vertaa;
};

template <typename Vertaa>
struct RajatTiivis {
    int pienin, suurin;
    [[no_unique_address]] Vertaa vertaa;
};

static_assert(sizeof(Rajat<std::less<int>>) == 12);
static_assert(sizeof(RajatTiivis<std::less<int>>) == 8);
// @loppu tyhja

// @alku tasaus
// Oma välimuistirivi kullekin laskurille (vrt. väärä jakaminen).
struct alignas(64) Laskuri {
    std::int64_t arvo;
};
static_assert(sizeof(Laskuri) == 64);
// @loppu tasaus

int main()
{
    // @alku koot
    std::printf("Huono %zu, Hyva %zu tavua\n", sizeof(Huono), sizeof(Hyva));
    std::printf("std::optional<double> %zu, std::variant<int, double> %zu\n",
                sizeof(std::optional<double>),
                sizeof(std::variant<int, double>));
    std::printf("1000 Huono-oliota %zu tavua, Hyva-oliota %zu tavua\n",
                1000 * sizeof(Huono), 1000 * sizeof(Hyva));
    // @loppu koot

    // @alku vektoribool
    // std::vector<bool> pakkaa arvot biteiksi: alkio ei ole bool vaan
    // välityöolio (proxy), joka viittaa bittiin.
    std::vector<bool> liput(1000, false);
    auto eka = liput[0];       // ei kopio: viittaus bittiin
    eka = true;                // muuttaa vektoria!
    std::printf("liput[0] = %d, tavuja noin %zu\n",
                static_cast<int>(liput[0]), liput.capacity() / 8);
    // @loppu vektoribool
}
