// Pikaoppaan esimerkit. Jokainen osa on oma lyhyt kokonaisuutensa.
#include <algorithm>
#include <concepts>
#include <expected>
#include <format>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <print>
#include <ranges>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

// @alku tyyppi
struct Piste {
    double x = 0.0;   // jäsenten oletusarvot
    double y = 0.0;
    auto operator<=>(const Piste&) const = default;   // ==, <, ... valmiina
};
// @loppu tyyppi

// @alku luokka
class Tili {
public:
    explicit Tili(std::string omistaja) : omistaja_{std::move(omistaja)} {}
    void talleta(long senttia) { saldo_ += senttia; }
    long saldo() const { return saldo_; }
    const std::string& omistaja() const { return omistaja_; }

private:
    std::string omistaja_;   // nollan sääntö: ei omaa hajotinta
    long saldo_ = 0;
};
// @loppu luokka

// @alku virheet
enum class Virhe { tyhja, ei_luku };

std::expected<int, Virhe> jasenna(std::string_view s)
{
    if (s.empty()) {
        return std::unexpected{Virhe::tyhja};
    }
    int arvo = 0;
    for (char c : s) {
        if (c < '0' || c > '9') {
            return std::unexpected{Virhe::ei_luku};
        }
        arvo = arvo * 10 + (c - '0');
    }
    return arvo;
}
// @loppu virheet

// @alku mallit
template <typename T>
concept Lukuarvo = std::integral<T> || std::floating_point<T>;

auto summa(const std::ranges::range auto& r)
    requires Lukuarvo<std::ranges::range_value_t<decltype(r)>>
{
    std::ranges::range_value_t<decltype(r)> s{};
    for (const auto& x : r) {
        s += x;
    }
    return s;
}
// @loppu mallit

int main()
{
    // @alku alustus
    int n{};                                 // 0
    auto nimi = std::string{"Ada"};          // std::string
    const auto pisteet = std::vector{3, 1, 2};   // vector<int>, CTAD
    Piste p{.x = 1.0, .y = 2.0};             // nimetyt alustimet
    auto [x, y] = p;                         // rakenteinen sidonta
    std::println("{} {} {} {} {}", n, nimi, pisteet.size(), x, y);
    // @loppu alustus

    // @alku omistus
    auto tili = std::make_unique<Tili>("Grace");   // yksi omistaja
    auto jaettu = std::make_shared<Tili>("Linus"); // jaettu omistus
    std::weak_ptr<Tili> tarkkailija = jaettu;      // ei omista
    Tili& lainattu = *tili;                        // lainaus viittauksena
    lainattu.talleta(500);
    auto uusi_omistaja = std::move(tili);          // omistus siirtyy
    std::println("{} {} {}", uusi_omistaja->saldo(), tili == nullptr,
                 tarkkailija.lock()->omistaja());
    // @loppu omistus

    // @alku kokoelmat
    std::vector<std::string> sanat{"omena", "kiivi", "banaani", "kiivi"};
    std::ranges::sort(sanat);
    auto [alku, loppu] = std::ranges::unique(sanat);
    sanat.erase(alku, loppu);                       // poista kaksoiskappaleet
    auto pituus = [](const std::string& s) { return s.size(); };
    auto pitkat = sanat
                  | std::views::transform(pituus)
                  | std::views::filter([](auto k) { return k > 5; });
    std::map<std::string, int> laskuri;
    for (const auto& s : sanat) {
        ++laskuri[s];                               // [] lisää puuttuvan
    }
    std::println("{} {} {}", sanat.size(), std::ranges::distance(pitkat),
                 laskuri.contains("omena"));
    // @loppu kokoelmat

    // @alku lambdat
    int raja = 2;
    auto suurempi = [raja](int a) { return a > raja; };   // arvolla
    auto kasvata = [&n] { ++n; };                         // viittauksella
    auto seuraava = [i = 0]() mutable { return ++i; };    // oma tila
    kasvata();
    const auto lkm = std::ranges::count_if(pisteet, suurempi);
    const auto pienin = [&] {                             // IIFE
        auto kopio = pisteet;
        std::ranges::sort(kopio);
        return kopio.front();
    }();
    std::println("{} {} {} {}", n, lkm, seuraava(), pienin);
    // @loppu lambdat

    // @alku virheet-kaytto
    for (std::string_view s : {"42", "", "4x"}) {
        auto tulos = jasenna(s).transform([](int v) { return v * 2; });
        if (tulos) {
            std::println("'{}' -> {}", s, *tulos);
        } else {
            std::println("'{}' -> virhe {}", s,
                         static_cast<int>(tulos.error()));
        }
    }
    std::optional<int> ehka;   // ei arvoa
    std::println("{}", ehka.value_or(-1));
    // @loppu virheet-kaytto

    // @alku mallit-kaytto
    std::println("{} {}", summa(std::vector{1, 2, 3}),
                 summa(std::vector{0.5, 0.25}));
    // @loppu mallit-kaytto

    // @alku saikeet
    std::mutex lukko;
    long yhteensa = 0;
    {
        std::vector<std::jthread> saikeet;
        for (int s = 1; s <= 4; ++s) {
            saikeet.emplace_back([&lukko, &yhteensa, s] {
                std::scoped_lock l{lukko};   // vapautuu lohkon lopussa
                yhteensa += s;
            });
        }
    }   // jthread odottaa säikeet hajottimessa
    std::println("{}", yhteensa);
    // @loppu saikeet
}
