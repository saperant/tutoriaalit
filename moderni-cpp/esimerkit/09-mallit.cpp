#include <format>
#include <optional>
#include <print>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// @alku funktio
template <typename T>
T suurin(const T& a, const T& b)
{
    return a < b ? b : a;
}
// @loppu funktio

// @alku luokka
template <typename T>
class Pino {
public:
    Pino() = default;
    explicit Pino(std::vector<T> alkiot) : alkiot_{std::move(alkiot)} {}

    void lisaa(T arvo) { alkiot_.push_back(std::move(arvo)); }

    std::optional<T> ota()
    {
        if (alkiot_.empty()) {
            return std::nullopt;
        }
        T arvo = std::move(alkiot_.back());
        alkiot_.pop_back();
        return arvo;
    }

    std::size_t koko() const { return alkiot_.size(); }

private:
    std::vector<T> alkiot_;
};
// @loppu luokka

// @alku constexpr-if
template <typename T>
std::string kuvaile(const T& arvo)
{
    if constexpr (std::is_integral_v<T>) {
        return std::format("kokonaisluku {}", arvo);
    } else if constexpr (std::is_floating_point_v<T>) {
        return std::format("liukuluku {}", arvo);
    } else {
        return "jokin muu: " + std::string{arvo};
    }
}
// @loppu constexpr-if

// @alku lyhennetty
void tulosta_pari(const auto& a, const auto& b)
{
    std::println("({}, {})", a, b);
}
// @loppu lyhennetty

int main()
{
    // @alku kaytto
    std::println("{} {}", suurin(3, 7), suurin<double>(2, 2.5));
    std::println("{}", suurin(std::string{"abc"}, std::string{"abd"}));

    Pino<std::string> sanat;
    sanat.lisaa("eka");
    sanat.lisaa("toka");
    auto paallimmainen = sanat.ota();
    std::println("{} {}", paallimmainen.value_or("-"), sanat.koko());

    Pino luvut{std::vector{1, 2, 3}};   // CTAD: Pino<int>
    std::println("{}", luvut.ota().value_or(0));

    std::println("{}", kuvaile(42));
    std::println("{}", kuvaile(0.5));
    std::println("{}", kuvaile("teksti"));

    tulosta_pari(1, "yksi");
    // @loppu kaytto
}
