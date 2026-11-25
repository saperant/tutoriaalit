// Resurssivälimuisti ja kuumalataus: sama tiedosto ladataan vain kerran,
// ja muuttunut tiedosto ladataan uudelleen pelin ollessa käynnissä.
#include <chrono>
#include <filesystem>
#include <fstream>
#include <map>
#include <memory>
#include <print>
#include <sstream>
#include <string>

namespace fs = std::filesystem;

// Resurssi: tässä vihollistyypin arvot tekstitiedostosta.
struct Vihollistyyppi {
    int kesto = 0;
    double nopeus = 0.0;
};

Vihollistyyppi lue(const fs::path& polku) {
    std::ifstream f(polku);
    Vihollistyyppi v;
    std::string avain;
    while (f >> avain) {
        if (avain == "kesto") {
            f >> v.kesto;
        } else if (avain == "nopeus") {
            f >> v.nopeus;
        }
    }
    return v;
}

// @alku valimuisti
class Resurssit {
public:
    // Kaikki käyttäjät saavat saman jaetun olion; kuumalataus päivittää
    // sen paikallaan, joten viittaukset pysyvät voimassa.
    std::shared_ptr<Vihollistyyppi> hae(const fs::path& polku) {
        auto& r = taulu_[polku];
        if (!r.arvo) {
            r.arvo = std::make_shared<Vihollistyyppi>(lue(polku));
            r.muokattu = fs::last_write_time(polku);
            ++latauksia;
        }
        return r.arvo;
    }

    // Kutsutaan esim. kerran sekunnissa kehitysversiossa.
    int tarkista_muutokset() {
        int ladattu = 0;
        for (auto& [polku, r] : taulu_) {
            const auto aika = fs::last_write_time(polku);
            if (aika != r.muokattu) {
                *r.arvo = lue(polku);
                r.muokattu = aika;
                ++ladattu;
            }
        }
        return ladattu;
    }

    int latauksia = 0;

private:
    struct Rivi {
        std::shared_ptr<Vihollistyyppi> arvo;
        fs::file_time_type muokattu;
    };
    std::map<fs::path, Rivi> taulu_;
};
// @loppu valimuisti

int main() {
    std::ofstream("orkki.txt") << "kesto 30\nnopeus 1.5\n";
    Resurssit resurssit;
    auto a = resurssit.hae("orkki.txt");
    auto b = resurssit.hae("orkki.txt");  // välimuistista
    std::println("latauksia {}, sama olio: {}", resurssit.latauksia,
                 a == b);
    std::println("orkki: kesto {}, nopeus {:.1f}", a->kesto, a->nopeus);

    // Suunnittelija muokkaa tiedostoa pelin ollessa käynnissä.
    std::ofstream("orkki.txt") << "kesto 45\nnopeus 1.2\n";
    // Tiedostojärjestelmän aikaleiman tarkkuus voi olla karkea, joten
    // esimerkki siirtää aikaleimaa varmuuden vuoksi.
    fs::last_write_time("orkki.txt", fs::last_write_time("orkki.txt") +
                                         std::chrono::seconds(1));
    std::println("uudelleen ladattu {}", resurssit.tarkista_muutokset());
    std::println("orkki: kesto {}, nopeus {:.1f}", b->kesto, b->nopeus);
}
