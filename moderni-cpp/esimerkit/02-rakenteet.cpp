#include <map>
#include <print>
#include <string>
#include <utility>

// @alku enum
enum class Vari { punainen, vihrea, sininen };
enum class Liikennevalo { punainen, keltainen, vihrea };
// @loppu enum

// @alku using
using Hinnasto = std::map<std::string, double>;
// @loppu using

// @alku pari
std::pair<int, int> jako(int jaettava, int jakaja)
{
    return {jaettava / jakaja, jaettava % jakaja};
}
// @loppu pari

int main()
{
    // @alku sidonnat
    auto [osamaara, jakojaannos] = jako(17, 5);
    std::println("17 / 5 = {}, jakojäännös {}", osamaara, jakojaannos);

    Hinnasto hinnat{{"kahvi", 2.5}, {"tee", 2.0}, {"pulla", 3.2}};
    for (const auto& [tuote, hinta] : hinnat) {
        std::println("{:<6} {:>5.2f} €", tuote, hinta);
    }
    // @loppu sidonnat

    // @alku ehtoalustus
    if (auto it = hinnat.find("tee"); it != hinnat.end()) {
        std::println("Tee maksaa {} €.", it->second);
    } else {
        std::println("Teetä ei ole.");
    }
    // it ei ole näkyvissä täällä.
    // @loppu ehtoalustus

    // @alku vertailu
    Vari v = Vari::punainen;
    Liikennevalo l = Liikennevalo::punainen;
    int i = static_cast<int>(v);
    std::println("{} {}", i, static_cast<int>(l));
    // @loppu vertailu

    // @alku nullptr
    int* osoitin = nullptr;
    if (osoitin == nullptr) {
        std::println("Osoitin ei osoita mihinkään.");
    }
    // @loppu nullptr
}
