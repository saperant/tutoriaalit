// Funktion välittäminen: malliparametri, funktio-osoitin, std::function.
#include <cstddef>
#include <functional>
#include <span>
#include <string_view>
#include <vector>

#include "mittari.hpp"
#include "satunnainen.hpp"

// @alku tavat
// Malliparametri: jokaiselle ehdolle syntyy oma versio funktiosta, ja
// kääntäjä sisällyttää ehdon silmukkaan.
template <typename Ehto>
std::size_t laske_jos(std::span<const int> x, Ehto ehto)
{
    std::size_t n = 0;
    for (int v : x) {
        n += ehto(v) ? 1 : 0;
    }
    return n;
}

// Funktio-osoitin: yksi käännetty versio, epäsuora kutsu joka alkiolle.
[[gnu::noinline]] std::size_t laske_osoitin(std::span<const int> x,
                                            bool (*ehto)(int))
{
    std::size_t n = 0;
    for (int v : x) {
        n += ehto(v) ? 1 : 0;
    }
    return n;
}

// std::function: tyyppien pyyhintä; mikä tahansa kutsuttava kelpaa,
// myös tilaa kantava lambda, mutta kutsu on aina epäsuora.
[[gnu::noinline]] std::size_t laske_function(
    std::span<const int> x, const std::function<bool(int)>& ehto)
{
    std::size_t n = 0;
    for (int v : x) {
        n += ehto(v) ? 1 : 0;
    }
    return n;
}
// @loppu tavat

bool suuri(int v) { return v > 500; }

// Mallin instanssi omana funktionaan, jotta sen voi tunnistaa
// konekoodista ja profiilista.
[[gnu::noinline]] std::size_t laske_malli(std::span<const int> x, int raja)
{
    return laske_jos(x, [raja](int v) { return v > raja; });
}

template <typename Toimi>
void valitse(std::string_view tapa, std::span<const int> x, Toimi toimi)
{
    int raja = 500;
    mittari::piilota(raja);
    if (tapa == "malli") {
        toimi([&] { mittari::pida(laske_malli(x, raja)); });
    } else if (tapa == "osoitin") {
        toimi([&] { mittari::pida(laske_osoitin(x, suuri)); });
    } else if (tapa == "function") {
        std::function<bool(int)> ehto = [raja](int v) { return v > raja; };
        toimi([&] { mittari::pida(laske_function(x, ehto)); });
    }
}

std::vector<int> luo(std::size_t n)
{
    Satunnainen s{3};
    std::vector<int> x(n);
    for (int& v : x) {
        v = static_cast<int>(s.alle(1000));
    }
    return x;
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    if (tila.mittaa) {
        auto x = luo(10'000'000);
        std::printf("ehdon tayttavien laskenta, 10000000 alkiota\n");
        double vertailu = 0;
        for (std::string_view t : {"function", "osoitin", "malli"}) {
            valitse(t, x, [&](auto f) {
                auto m = mittari::mittaa(f, 11);
                mittari::tulosta(t, m, vertailu);
                vertailu = vertailu == 0 ? m.mediaani_ms : vertailu;
            });
        }
        return 0;
    }
    auto x = luo(1000);
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, x, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    std::function<bool(int)> ehto = [](int v) { return v > 500; };
    std::printf("yli 500: malli %zu, osoitin %zu, function %zu\n",
                laske_malli(x, 500), laske_osoitin(x, suuri),
                laske_function(x, ehto));
}
