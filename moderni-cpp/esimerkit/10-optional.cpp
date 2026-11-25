#include <charconv>
#include <optional>
#include <print>
#include <string_view>

// @alku jasenna
std::optional<int> jasenna(std::string_view teksti)
{
    int arvo{};
    auto [loppu, virhe] = std::from_chars(
        teksti.data(), teksti.data() + teksti.size(), arvo);
    if (virhe != std::errc{} || loppu != teksti.data() + teksti.size()) {
        return std::nullopt;
    }
    return arvo;
}
// @loppu jasenna

// @alku ketju
std::optional<int> positiivinen(int x)
{
    if (x > 0) {
        return x;
    }
    return std::nullopt;
}
// @loppu ketju

int main()
{
    // @alku kaytto
    for (std::string_view s : {"42", "-7", "12abc", ""}) {
        if (auto luku = jasenna(s)) {
            std::println("'{}' -> {}", s, *luku);
        } else {
            std::println("'{}' -> ei luku", s);
        }
    }
    std::println("oletusarvolla: {}", jasenna("x").value_or(0));
    // @loppu kaytto

    // @alku monadinen
    for (std::string_view s : {"21", "-3", "abc"}) {
        auto tulos = jasenna(s)
                         .and_then(positiivinen)
                         .transform([](int x) { return x * 2; });
        std::println("{}: {}", s, tulos.value_or(-1));
    }
    // @loppu monadinen
}
