// Muotoilun hinta: kokonaisluku merkkijonoksi kuudella tavalla.
#include <array>
#include <charconv>
#include <cstdio>
#include <format>
#include <sstream>
#include <string>
#include <string_view>

#include "laskuri.hpp"
#include "mittari.hpp"

// @alku tavat
// Kukin tapa muuntaa luvun ja palauttaa merkkien määrän.
std::size_t snprintf_tapa(int x)
{
    std::array<char, 16> p;
    return static_cast<std::size_t>(
        std::snprintf(p.data(), p.size(), "%d", x));
}

std::size_t to_chars_tapa(int x)
{
    std::array<char, 16> p;
    auto [loppu, virhe] = std::to_chars(p.data(), p.data() + p.size(), x);
    return static_cast<std::size_t>(loppu - p.data());
}

std::size_t format_to_tapa(int x)
{
    std::array<char, 16> p;
    auto tulos = std::format_to_n(p.data(), p.size(), "{}", x);
    return static_cast<std::size_t>(tulos.size);
}

std::size_t format_tapa(int x) { return std::format("{}", x).size(); }

std::size_t to_string_tapa(int x) { return std::to_string(x).size(); }

std::size_t ostringstream_tapa(int x)
{
    std::ostringstream virta;
    virta << x;
    return virta.str().size();
}
// @loppu tavat

using Tapa = std::size_t (*)(int);

struct Nimetty {
    std::string_view nimi;
    Tapa tapa;
};

constexpr std::array<Nimetty, 6> tavat{{
    {"snprintf", snprintf_tapa},
    {"to_chars", to_chars_tapa},
    {"format_to_n", format_to_tapa},
    {"format", format_tapa},
    {"to_string", to_string_tapa},
    {"ostringstream", ostringstream_tapa},
}};

// @alku kierros
// Yksi kierros: tuhat eri lukua, jotta haarautumisen ennustin ja
// välimuisti eivät näe samaa syötettä joka kerta.
[[gnu::noinline]] std::size_t kierros(Tapa tapa)
{
    std::size_t merkit = 0;
    for (int i = 0; i < 1000; ++i) {
        int x = i * 7919 - 3'000'000;
        mittari::piilota(x);
        merkit += tapa(x);
    }
    return merkit;
}
// @loppu kierros

// @alku vertailu
// Nanosekuntia kutsua kohden: kalibroitu mittaus (mittari.hpp) ajaa
// kierrosta, jossa on tuhat kutsua.
double ns_per_kutsu(Tapa tapa)
{
    return mittari::ns_per_toisto([&] { mittari::pida(kierros(tapa)); })
           / 1000.0;
}
// @loppu vertailu

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    if (tila.mittaa) {
        std::printf("kokonaisluku merkkijonoksi, ns/kutsu (paras 5:sta)\n");
        for (const auto& [nimi, tapa] : tavat) {
            double paras = 1e300;
            for (int k = 0; k < 5; ++k) {
                paras = std::min(paras, ns_per_kutsu(tapa));
            }
            std::printf("  %-14.*s %7.1f ns\n",
                        static_cast<int>(nimi.size()), nimi.data(), paras);
        }
        return 0;
    }
    if (!tila.kerran.empty()) {
        for (const auto& [nimi, tapa] : tavat) {
            if (nimi == tila.kerran) {
                for (long i = 0; i < tila.n; ++i) {
                    mittari::pida(kierros(tapa));
                }
            }
        }
        return 0;
    }
    // @alku testi
    for (const auto& [nimi, tapa] : tavat) {
        laskuri::Jakso j;
        std::size_t merkit = kierros(tapa);
        std::printf("  %-14.*s merkkeja %zu, varauksia %zu\n",
                    static_cast<int>(nimi.size()), nimi.data(), merkit,
                    j.varaukset());
    }
    // @loppu testi
}
