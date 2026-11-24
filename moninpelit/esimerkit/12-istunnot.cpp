// Pelisession elinkaari palvelimella tilakoneena: jono, lataus, peli,
// katkenneen yhteyden armonaika ja päättyminen. Ajastimet ovat
// palvelimen kellossa, eivät asiakkaan.
#include <cstdint>
#include <iterator>
#include <print>
#include <string_view>
#include <utility>

// @alku tilat
enum class Tila { Jonossa, Ladataan, Pelissa, Katkennut, Paattynyt };

constexpr std::string_view nimi(Tila t) {
    constexpr std::string_view nimet[] = {"jonossa", "ladataan", "pelissä",
                                          "katkennut", "päättynyt"};
    return nimet[static_cast<int>(t)];
}

enum class Tapahtuma { OtteluLoytyi, Ladattu, YhteysKatkesi, Palasi,
                       PeliLoppui, Aika };

struct Sessio {
    Tila tila = Tila::Jonossa;
    std::int64_t takaraja = 0;  // tilan aikaraja palvelimen kellossa

    void kasittele(Tapahtuma e, std::int64_t nyt) {
        const Tila ennen = tila;
        switch (tila) {
        case Tila::Jonossa:
            if (e == Tapahtuma::OtteluLoytyi) {
                siirry(Tila::Ladataan, nyt + 30'000);  // 30 s latausaikaa
            }
            break;
        case Tila::Ladataan:
            if (e == Tapahtuma::Ladattu) {
                siirry(Tila::Pelissa, 0);
            } else if (e == Tapahtuma::Aika) {
                siirry(Tila::Jonossa, 0);  // ottelu perutaan, takaisin jonoon
            }
            break;
        case Tila::Pelissa:
            if (e == Tapahtuma::YhteysKatkesi) {
                siirry(Tila::Katkennut, nyt + 60'000);  // armonaika
            } else if (e == Tapahtuma::PeliLoppui) {
                siirry(Tila::Paattynyt, 0);
            }
            break;
        case Tila::Katkennut:
            if (e == Tapahtuma::Palasi) {
                siirry(Tila::Pelissa, 0);  // sama paikka, sama tila
            } else if (e == Tapahtuma::Aika || e == Tapahtuma::PeliLoppui) {
                siirry(Tila::Paattynyt, 0);  // kirjataan keskeytykseksi
            }
            break;
        case Tila::Paattynyt:
            break;
        }
        if (tila != ennen) {
            std::println("{:>6} ms: {} -> {}", nyt, nimi(ennen), nimi(tila));
        }
    }
    // Palvelin kutsuu joka tikki: vanhentunut takaraja on tapahtuma.
    void tikki(std::int64_t nyt) {
        if (takaraja != 0 && nyt >= takaraja) {
            kasittele(Tapahtuma::Aika, nyt);
        }
    }

private:
    void siirry(Tila uusi, std::int64_t raja) {
        tila = uusi;
        takaraja = raja;
    }
};
// @loppu tilat

int main() {
    Sessio s;
    const std::pair<std::int64_t, Tapahtuma> kulku[] = {
        {1'000, Tapahtuma::OtteluLoytyi},
        {9'000, Tapahtuma::Ladattu},
        {200'000, Tapahtuma::YhteysKatkesi},
        {215'000, Tapahtuma::Palasi},
        {400'000, Tapahtuma::YhteysKatkesi},
    };
    std::size_t i = 0;
    for (std::int64_t nyt = 0; nyt <= 600'000; nyt += 50) {
        while (i < std::size(kulku) && kulku[i].first == nyt) {
            s.kasittele(kulku[i++].second, nyt);
        }
        s.tikki(nyt);
    }
}
