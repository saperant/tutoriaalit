#include <print>
#include <string>
#include <string_view>

// @alku funktio
// Hyväksyy std::stringin, literaalin ja toisen string_view'n
// ilman kopiointia.
std::string_view tiedostopaate(std::string_view polku)
{
    auto piste = polku.rfind('.');
    if (piste == std::string_view::npos) {
        return {};
    }
    return polku.substr(piste + 1);
}
// @loppu funktio

int main()
{
    // @alku kaytto
    std::string polku = "raportit/vuosi.pdf";
    std::println("{}", tiedostopaate(polku));
    std::println("{}", tiedostopaate("kuva.png"));
    std::println("[{}]", tiedostopaate("README"));
    // @loppu kaytto

    // @alku metodit
    std::string_view rivi = "ERROR: levy täynnä";
    std::println("{} {} {}", rivi.starts_with("ERROR"),
                 rivi.ends_with("täynnä"), rivi.contains("levy"));
    // @loppu metodit

    // @alku literaalit
    using namespace std::literals;
    auto s = "std::string"s;
    auto sv = "std::string_view"sv;
    std::println("{} {}", s.size(), sv.size());
    // @loppu literaalit
}
