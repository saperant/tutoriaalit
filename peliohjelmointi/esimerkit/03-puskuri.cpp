// Hypyn puskurointi ja "kojoottiaika": pelaaja hyppää, vaikka painallus
// tulee muutaman ruudun liian aikaisin tai reunalta pudottua.
#include <print>
#include <string_view>
#include <vector>

// @alku armo
struct Hyppaaja {
    int ruutuja_ilmassa = 1000;  // 0 = maassa
    int ruutuja_painalluksesta = 1000;
    int armo = 0;                // sallittu myöhästyminen ruutuina

    // Kutsutaan kerran ruudussa; palauttaa true, jos hyppy alkaa.
    bool paivita(bool maassa, bool hyppy_painettu) {
        ruutuja_ilmassa = maassa ? 0 : ruutuja_ilmassa + 1;
        ruutuja_painalluksesta =
            hyppy_painettu ? 0 : ruutuja_painalluksesta + 1;
        const bool saa_hypata = ruutuja_ilmassa <= armo;  // kojootti
        const bool haluaa = ruutuja_painalluksesta <= armo;  // puskuri
        if (saa_hypata && haluaa) {
            ruutuja_painalluksesta = 1000;  // painallus käytetty
            ruutuja_ilmassa = armo + 1;      // ei toista hyppyä heti
            return true;
        }
        return false;
    }
};
// @loppu armo

// Maaprofiili: '#' = jalat maassa, '.' = ilmassa.
// Painallukset: '^' = hyppy painettu tällä ruudulla.
int hypyn_ruutu(std::string_view maa, std::string_view napit, int armo) {
    Hyppaaja h;
    h.armo = armo;
    for (std::size_t i = 0; i < maa.size(); ++i) {
        if (h.paivita(maa[i] == '#', napit[i] == '^')) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

int main() {
    struct Tapaus {
        std::string_view nimi, maa, napit;
    };
    const std::vector<Tapaus> tapaukset = {
        {"ajoissa", "######....", "....^....."},
        {"reunan jälkeen", "######....", ".......^.."},
        {"liian aikaisin", "....######", "..^......."},
    };
    for (const auto& t : tapaukset) {
        std::println("{:<14}: ilman armoa {:2}, armo 3 ruutua {:2}", t.nimi,
                     hypyn_ruutu(t.maa, t.napit, 0),
                     hypyn_ruutu(t.maa, t.napit, 3));
    }
}
