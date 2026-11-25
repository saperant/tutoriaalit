// Välitön käyttöliittymä (immediate mode): painikkeet kuvataan joka
// ruudulla koodissa, ja painallus palautetaan suoraan kutsujalle.
// Käyttöliittymällä ei ole omaa pysyvää oliopuuta.
#include <print>
#include <string>
#include <string_view>
#include <vector>

struct Hiiri {
    int x = 0, y = 0;
    bool alhaalla = false, edellinen = false;
};

// @alku valiton
class Ui {
public:
    explicit Ui(const Hiiri& h) : hiiri_(h) {}

    // Painike piirretään (tässä: lisätään piirtolistaan) ja sen tila
    // lasketaan samalla kertaa. Palauttaa true, kun painike vapautetaan
    // sen päällä.
    bool painike(std::string_view teksti, int x, int y, int w, int h) {
        const bool paalla = hiiri_.x >= x && hiiri_.x < x + w &&
                            hiiri_.y >= y && hiiri_.y < y + h;
        const bool painettu = paalla && hiiri_.edellinen &&
                              !hiiri_.alhaalla;
        piirtolista.push_back(std::string(teksti) +
                              (paalla ? (hiiri_.alhaalla ? " [alas]"
                                                         : " [päällä]")
                                      : ""));
        return painettu;
    }

    std::vector<std::string> piirtolista;

private:
    const Hiiri& hiiri_;
};
// @loppu valiton

int main() {
    int aanenvoimakkuus = 5;
    bool pelissa = false;
    const std::vector<Hiiri> ruudut = {
        {10, 10, false, false}, {10, 10, true, false},
        {10, 10, false, true},  {110, 10, true, false},
        {110, 10, false, true},
    };
    for (std::size_t i = 0; i < ruudut.size(); ++i) {
        // @alku valikko
        Ui ui(ruudut[i]);
        if (ui.painike("Aloita", 0, 0, 100, 30)) {
            pelissa = true;
        }
        if (ui.painike("Ääni +", 100, 0, 60, 30)) {
            ++aanenvoimakkuus;
        }
        // @loppu valikko
        std::print("ruutu {}:", i);
        for (const auto& rivi : ui.piirtolista) {
            std::print(" {} |", rivi);
        }
        std::println(" pelissä {}, ääni {}", pelissa, aanenvoimakkuus);
    }
}
