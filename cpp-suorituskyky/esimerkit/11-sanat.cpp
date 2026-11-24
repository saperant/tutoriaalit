// Tapaustutkimus: sanojen esiintymät tekstissä neljässä vaiheessa.
#include <algorithm>
#include <cstddef>
#include <functional>
#include <map>
#include <sstream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

#include "laskuri.hpp"
#include "mittari.hpp"
#include "satunnainen.hpp"

using Tulos = std::vector<std::pair<std::string, int>>;

// Yleisimmät ensin; tasatilanteessa aakkosjärjestys.
bool yleisempi(const auto& a, const auto& b)
{
    return a.second != b.second ? a.second > b.second : a.first < b.first;
}

// @alku v1
// Vaihe 1: virta jäsentää sanat, puu laskee ne, ja kaikki lajitellaan.
Tulos yleisimmat_v1(const std::string& teksti, std::size_t k)
{
    std::istringstream virta{teksti};
    std::map<std::string, int> maarat;
    std::string sana;
    while (virta >> sana) {
        ++maarat[sana];
    }
    Tulos kaikki(maarat.begin(), maarat.end());
    std::ranges::sort(kaikki, [](const auto& a, const auto& b) {
        return yleisempi(a, b);
    });
    kaikki.resize(std::min(k, kaikki.size()));
    return kaikki;
}
// @loppu v1

// @alku pilko
// Kutsuu funktiota jokaiselle välilyönneillä erotetulle sanalle.
template <typename F>
void jokaiselle_sanalle(std::string_view teksti, F f)
{
    std::size_t i = 0;
    while (i < teksti.size()) {
        while (i < teksti.size() && teksti[i] == ' ') {
            ++i;
        }
        std::size_t alku = i;
        while (i < teksti.size() && teksti[i] != ' ') {
            ++i;
        }
        if (i > alku) {
            f(teksti.substr(alku, i - alku));
        }
    }
}
// @loppu pilko

// @alku v2
// Vaihe 2: oma pilkkoja ja hajautustaulu. Avain rakennetaan
// std::stringiksi joka haussa, myös silloin kun sana on jo taulussa.
Tulos yleisimmat_v2(const std::string& teksti, std::size_t k)
{
    std::unordered_map<std::string, int> maarat;
    jokaiselle_sanalle(teksti, [&](std::string_view s) {
        ++maarat[std::string{s}];
    });
    Tulos kaikki(maarat.begin(), maarat.end());
    std::ranges::sort(kaikki, [](const auto& a, const auto& b) {
        return yleisempi(a, b);
    });
    kaikki.resize(std::min(k, kaikki.size()));
    return kaikki;
}
// @loppu v2

// @alku v3
// Vaihe 3: heterogeeninen haku. Läpinäkyvä hajautin ja vertailija
// (is_transparent) sallivat haun string_view-avaimella, joten
// std::string rakennetaan vain uudelle sanalle.
struct MerkkijonoHajautin {
    using is_transparent = void;
    std::size_t operator()(std::string_view s) const
    {
        return std::hash<std::string_view>{}(s);
    }
};

Tulos yleisimmat_v3(const std::string& teksti, std::size_t k)
{
    std::unordered_map<std::string, int, MerkkijonoHajautin,
                       std::equal_to<>> maarat;
    maarat.reserve(4096);
    jokaiselle_sanalle(teksti, [&](std::string_view s) {
        if (auto it = maarat.find(s); it != maarat.end()) {
            ++it->second;
        } else {
            maarat.emplace(s, 1);
        }
    });
    Tulos kaikki(maarat.begin(), maarat.end());
    std::ranges::sort(kaikki, [](const auto& a, const auto& b) {
        return yleisempi(a, b);
    });
    kaikki.resize(std::min(k, kaikki.size()));
    return kaikki;
}
// @loppu v3

// @alku v4
// Vaihe 4: avaimet ovat näkymiä tekstiin (teksti elää koko laskennan
// ajan), ja vain k yleisintä järjestetään.
Tulos yleisimmat_v4(const std::string& teksti, std::size_t k)
{
    std::unordered_map<std::string_view, int> maarat;
    maarat.reserve(4096);
    jokaiselle_sanalle(teksti, [&](std::string_view s) { ++maarat[s]; });
    std::vector<std::pair<std::string_view, int>> kaikki(maarat.begin(),
                                                         maarat.end());
    k = std::min(k, kaikki.size());
    std::ranges::partial_sort(kaikki, kaikki.begin() + static_cast<long>(k),
                              [](const auto& a, const auto& b) {
                                  return yleisempi(a, b);
                              });
    Tulos tulos;
    for (std::size_t i = 0; i < k; ++i) {
        tulos.emplace_back(std::string{kaikki[i].first}, kaikki[i].second);
    }
    return tulos;
}
// @loppu v4

// Lokitiedoston kaltainen teksti: sanat ovat yli 15 merkin tunnisteita
// (eivät mahdu lyhyen merkkijonon puskuriin), ja niiden jakauma on vino.
std::string luo_teksti(std::size_t sanoja)
{
    static constexpr std::string_view tavut[] = {
        "ka", "lo", "mi", "su", "te", "va", "ri", "no", "pe", "ju"};
    Satunnainen s{2};
    std::string teksti;
    for (std::size_t i = 0; i < sanoja; ++i) {
        auto n = s.alle(1 + s.alle(3000));
        std::string sana;
        do {
            sana += tavut[n % 10];
            n /= 10;
        } while (n > 0);
        teksti += sana + "_tunnistesana ";
    }
    return teksti;
}

template <typename Toimi>
void valitse(std::string_view tapa, const std::string& teksti, Toimi toimi)
{
    using Funktio = Tulos (*)(const std::string&, std::size_t);
    Funktio f = tapa == "v1"   ? yleisimmat_v1
                : tapa == "v2" ? yleisimmat_v2
                : tapa == "v3" ? yleisimmat_v3
                               : yleisimmat_v4;
    toimi([&] { mittari::pida(f(teksti, 10)); });
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    std::size_t sanoja = tila.mittaa ? 1'000'000 : 20'000;
    auto teksti = luo_teksti(sanoja);
    if (tila.mittaa) {
        std::printf("10 yleisinta sanaa, %zu sanaa\n", sanoja);
        double vertailu = 0;
        for (std::string_view t : {"v1", "v2", "v3", "v4"}) {
            valitse(t, teksti, [&](auto f) {
                auto m = mittari::mittaa(f, 11);
                mittari::tulosta(t, m, vertailu);
                vertailu = vertailu == 0 ? m.mediaani_ms : vertailu;
            });
        }
        return 0;
    }
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, teksti, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    // @alku testi
    Tulos tulokset[4];
    std::size_t varaukset[4];
    auto versiot = {yleisimmat_v1, yleisimmat_v2, yleisimmat_v3,
                    yleisimmat_v4};
    std::size_t i = 0;
    for (auto versio : versiot) {
        laskuri::Jakso j;
        tulokset[i] = versio(teksti, 10);
        varaukset[i++] = j.varaukset();
    }
    for (const auto& [sana, maara] : tulokset[0]) {
        std::printf("  %-18s %d\n", sana.c_str(), maara);
    }
    bool samat = std::ranges::all_of(tulokset, [&](const Tulos& t) {
        return t == tulokset[0];
    });
    std::printf("kaikki versiot samaa mielta: %s\n", samat ? "kylla" : "ei");
    std::printf("varauksia: v1 %zu, v2 %zu, v3 %zu, v4 %zu\n", varaukset[0],
                varaukset[1], varaukset[2], varaukset[3]);
    // @loppu testi
}
