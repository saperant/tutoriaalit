#include <charconv>
#include <iostream>
#include <optional>
#include <print>
#include <string>
#include <string_view>
#include <system_error>

// @alku rivi
struct Tilausrivi {
    std::string tuote;
    int maara;
    double hinta;
};

// Jakaa näkymän ensimmäisen erottimen kohdalta: palauttaa osan ennen
// erotinta ja siirtää näkymän erottimen ohi.
std::string_view seuraava_kentta(std::string_view& loput, char erotin)
{
    auto kohta = loput.find(erotin);
    auto kentta = loput.substr(0, kohta);
    loput = kohta == std::string_view::npos ? std::string_view{}
                                            : loput.substr(kohta + 1);
    return kentta;
}

template <typename T>
std::optional<T> luku(std::string_view s)
{
    T arvo{};
    auto [loppu, virhe] = std::from_chars(s.data(), s.data() + s.size(),
                                          arvo);
    if (virhe != std::errc{} || loppu != s.data() + s.size()) {
        return std::nullopt;
    }
    return arvo;
}

std::optional<Tilausrivi> jasenna(std::string_view rivi)
{
    auto tuote = seuraava_kentta(rivi, ';');
    auto maara = luku<int>(seuraava_kentta(rivi, ';'));
    auto hinta = luku<double>(seuraava_kentta(rivi, ';'));
    if (tuote.empty() || !maara || !hinta || !rivi.empty() || *maara <= 0) {
        return std::nullopt;
    }
    return Tilausrivi{std::string{tuote}, *maara, *hinta};
}
// @loppu rivi

int main()
{
    // @alku luku
    std::string rivi;
    int rivinro = 0;
    double yhteensa = 0.0;
    while (std::getline(std::cin, rivi)) {
        ++rivinro;
        if (rivi.empty() || rivi.starts_with('#')) {
            continue;   // tyhjät ja kommenttirivit ohitetaan
        }
        auto t = jasenna(rivi);
        if (!t) {
            std::println(std::cerr, "rivi {}: virheellinen: '{}'",
                         rivinro, rivi);
            continue;
        }
        std::println("{:<10} {:>3} x {:>6.2f}", t->tuote, t->maara, t->hinta);
        yhteensa += t->maara * t->hinta;
    }
    std::println("yhteensä {:.2f}", yhteensa);
    // @loppu luku
}
