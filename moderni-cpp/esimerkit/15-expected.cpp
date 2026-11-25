#include <charconv>
#include <expected>
#include <print>
#include <string>
#include <string_view>

// @alku tyypit
enum class Virhe { tyhja, ei_luku, alueen_ulkopuolella };

std::string_view kuvaus(Virhe v)
{
    switch (v) {
    case Virhe::tyhja: return "tyhjä syöte";
    case Virhe::ei_luku: return "ei luku";
    case Virhe::alueen_ulkopuolella: return "alueen ulkopuolella";
    }
    return "tuntematon";
}
// @loppu tyypit

// @alku jasenna
std::expected<int, Virhe> jasenna(std::string_view s)
{
    if (s.empty()) {
        return std::unexpected{Virhe::tyhja};
    }
    int arvo{};
    auto [loppu, ec] = std::from_chars(s.data(), s.data() + s.size(), arvo);
    if (ec != std::errc{} || loppu != s.data() + s.size()) {
        return std::unexpected{Virhe::ei_luku};
    }
    return arvo;
}

std::expected<int, Virhe> tarkista_portti(int portti)
{
    if (portti < 1 || portti > 65535) {
        return std::unexpected{Virhe::alueen_ulkopuolella};
    }
    return portti;
}
// @loppu jasenna

int main()
{
    // @alku kaytto
    for (std::string_view syote : {"8080", "", "http", "70000"}) {
        auto portti = jasenna(syote).and_then(tarkista_portti);
        if (portti) {
            std::println("'{}': portti {}", syote, *portti);
        } else {
            std::println("'{}': {}", syote, kuvaus(portti.error()));
        }
    }
    // @loppu kaytto

    // @alku ketju
    auto osoite = jasenna("443")
                      .and_then(tarkista_portti)
                      .transform([](int p) {
                          return "localhost:" + std::to_string(p);
                      })
                      .value_or("ei osoitetta");
    std::println("{}", osoite);
    // @loppu ketju
}
