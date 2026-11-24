// Virtuaalikutsut, devirtualisointi, std::variant ja CRTP.
#include <cmath>
#include <cstddef>
#include <memory>
#include <numbers>
#include <span>
#include <string_view>
#include <variant>
#include <vector>

#include "laskuri.hpp"
#include "mittari.hpp"
#include "satunnainen.hpp"

// @alku hierarkia
class Kuvio {
public:
    virtual ~Kuvio() = default;
    virtual double pinta_ala() const = 0;
};

class Ympyra : public Kuvio {
public:
    explicit Ympyra(double r) : r_{r} {}
    double pinta_ala() const override { return std::numbers::pi * r_ * r_; }

private:
    double r_;
};

class Suorakulmio : public Kuvio {
public:
    Suorakulmio(double l, double k) : l_{l}, k_{k} {}
    double pinta_ala() const override { return l_ * k_; }

private:
    double l_, k_;
};
// @loppu hierarkia

// @alku virtuaali
// Jokainen kutsu haetaan olion virtuaalitaulusta: epäsuora hyppy, jota
// kääntäjä ei voi sisällyttää, koska kohde selviää vasta ajon aikana.
[[gnu::noinline]] double summa_virtuaali(
    std::span<const std::unique_ptr<Kuvio>> kuviot)
{
    double s = 0;
    for (const auto& k : kuviot) {
        s += k->pinta_ala();
    }
    return s;
}
// @loppu virtuaali

// @alku final
// Ilman final-merkintää Ympyra-viittaus voi osoittaa aliluokkaan, joka
// korvaa pinta_ala-funktion, joten kutsu on yhä virtuaalinen.
class YmpyraFinal final : public Kuvio {
public:
    explicit YmpyraFinal(double r) : r_{r} {}
    double pinta_ala() const override { return std::numbers::pi * r_ * r_; }

private:
    double r_;
};

[[gnu::noinline]] double summa_avoin(std::span<const Ympyra> ympyrat)
{
    double s = 0;
    for (const Ympyra& y : ympyrat) {
        s += y.pinta_ala();        // virtuaalinen kutsu
    }
    return s;
}

[[gnu::noinline]] double summa_final(std::span<const YmpyraFinal> ympyrat)
{
    double s = 0;
    for (const YmpyraFinal& y : ympyrat) {
        s += y.pinta_ala();        // suora kutsu, sisällytetään
    }
    return s;
}
// @loppu final

// @alku variant
// Suljettu joukko tyyppejä ilman perintää. Oliot ovat vektorissa
// peräkkäin, ja std::visit valitsee funktion tyyppitunnisteen mukaan.
struct YmpyraArvo {
    double r;
    double pinta_ala() const { return std::numbers::pi * r * r; }
};

struct SuorakulmioArvo {
    double l, k;
    double pinta_ala() const { return l * k; }
};

using KuvioArvo = std::variant<YmpyraArvo, SuorakulmioArvo>;

[[gnu::noinline]] double summa_variant(std::span<const KuvioArvo> kuviot)
{
    double s = 0;
    for (const auto& k : kuviot) {
        s += std::visit([](const auto& x) { return x.pinta_ala(); }, k);
    }
    return s;
}
// @loppu variant

// @alku crtp
// CRTP (curiously recurring template pattern): kantaluokka tuntee
// aliluokan tyyppiparametrina, joten "virtuaalinen" kutsu ratkeaa
// käännösaikana. Yhteistä säiliötä eri tyypeille ei voi tehdä.
template <typename Aliluokka>
struct KuvioPohja {
    double pinta_ala() const
    {
        return static_cast<const Aliluokka&>(*this).laske_ala();
    }
};

struct YmpyraCrtp : KuvioPohja<YmpyraCrtp> {
    double r;
    explicit YmpyraCrtp(double r_) : r{r_} {}
    double laske_ala() const { return std::numbers::pi * r * r; }
};

template <typename T>
[[gnu::noinline]] double summa_crtp(std::span<const T> kuviot)
{
    double s = 0;
    for (const auto& k : kuviot) {
        s += k.pinta_ala();
    }
    return s;
}
// @loppu crtp

struct Aineisto {
    std::vector<std::unique_ptr<Kuvio>> osoittimet;
    std::vector<KuvioArvo> arvot;
    std::vector<Ympyra> ympyrat;
    std::vector<YmpyraFinal> ympyrat_final;
    std::vector<YmpyraCrtp> ympyrat_crtp;
    std::size_t varaukset_osoittimet = 0;
    std::size_t varaukset_arvot = 0;
};

Aineisto luo(std::size_t n)
{
    Aineisto a;
    Satunnainen sat{7};
    a.osoittimet.reserve(n);
    a.arvot.reserve(n);
    for (std::size_t i = 0; i < n; ++i) {
        double x = 1 + sat.alle(10);
        double y = 1 + sat.alle(10);
        bool ympyra = sat.alle(2) == 0;
        laskuri::Jakso j1;
        if (ympyra) {
            a.osoittimet.push_back(std::make_unique<Ympyra>(x));
        } else {
            a.osoittimet.push_back(std::make_unique<Suorakulmio>(x, y));
        }
        a.varaukset_osoittimet += j1.varaukset();
        laskuri::Jakso j2;
        if (ympyra) {
            a.arvot.push_back(YmpyraArvo{x});
        } else {
            a.arvot.push_back(SuorakulmioArvo{x, y});
        }
        a.varaukset_arvot += j2.varaukset();
        a.ympyrat.emplace_back(x);
        a.ympyrat_final.emplace_back(x);
        a.ympyrat_crtp.emplace_back(x);
    }
    return a;
}

template <typename Toimi>
void valitse(std::string_view tapa, const Aineisto& a, Toimi toimi)
{
    if (tapa == "virtuaali") {
        toimi([&] { mittari::pida(summa_virtuaali(a.osoittimet)); });
    } else if (tapa == "variant") {
        toimi([&] { mittari::pida(summa_variant(a.arvot)); });
    } else if (tapa == "avoin") {
        toimi([&] { mittari::pida(summa_avoin(a.ympyrat)); });
    } else if (tapa == "final") {
        toimi([&] { mittari::pida(summa_final(a.ympyrat_final)); });
    } else if (tapa == "crtp") {
        toimi([&] {
            mittari::pida(summa_crtp<YmpyraCrtp>(a.ympyrat_crtp));
        });
    }
}

int main(int argc, char** argv)
{
    auto tila = mittari::lue_tila({argv, static_cast<std::size_t>(argc)});
    if (tila.mittaa) {
        auto a = luo(1'000'000);
        std::printf("pinta-alojen summa, 1000000 kuviota\n");
        for (std::string_view t :
             {"virtuaali", "variant", "avoin", "final", "crtp"}) {
            valitse(t, a, [&](auto f) {
                mittari::tulosta(t, mittari::mittaa(f, 11));
            });
        }
        return 0;
    }
    auto a = luo(1000);
    if (!tila.kerran.empty()) {
        valitse(tila.kerran, a, [&](auto f) {
            for (long i = 0; i < tila.n; ++i) {
                f();
            }
        });
        return 0;
    }
    // @alku testi
    double v = summa_virtuaali(a.osoittimet);
    double w = summa_variant(a.arvot);
    double y = summa_avoin(a.ympyrat);
    double f = summa_final(a.ympyrat_final);
    double c = summa_crtp<YmpyraCrtp>(a.ympyrat_crtp);
    std::printf("sekalaiset: virtuaali %.3f, variant %.3f\n", v, w);
    std::printf("ympyrat: avoin %.3f, final %.3f, crtp %.3f\n", y, f, c);
    std::printf("varauksia: osoittimet %zu, variant %zu\n",
                a.varaukset_osoittimet, a.varaukset_arvot);
    std::printf("koot: Ympyra %zu, KuvioArvo %zu tavua\n", sizeof(Ympyra),
                sizeof(KuvioArvo));
    // @loppu testi
}
