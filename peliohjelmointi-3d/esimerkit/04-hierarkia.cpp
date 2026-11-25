// Näkymäpuu: paikalliset muunnokset, maailmamatriisit, likaisuuslippu
// ja vanhemman vaihto niin, että kappale pysyy paikallaan maailmassa.
// Argumenttina annetulla nimellä tallennetaan kaksi kuvaa nosturista.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/mallit.hpp"
#include "yhteinen/tulostus.hpp"

#include <print>
#include <string>
#include <vector>

// @alku puu
struct Solmu {
    std::string nimi;
    int vanhempi = -1;  // -1 = juuri; vanhempi on taulukossa ennen lasta
    Muunnos paikallinen;
    Mat4 maailma = yksikko();
    bool likainen = true;  // paikallinen muunnos tai vanhempi on vaihtunut
};

class Nakymapuu {
public:
    int lisaa(std::string nimi, int vanhempi, const Muunnos& m) {
        solmut_.push_back({std::move(nimi), vanhempi, m});
        return static_cast<int>(solmut_.size()) - 1;
    }
    Muunnos& muokkaa(int i) {
        solmut_[i].likainen = true;
        return solmut_[i].paikallinen;
    }
    // Laskee muuttuneiden solmujen ja niiden jälkeläisten
    // maailmamatriisit yhdellä läpikäynnillä. Palauttaa laskettujen määrän.
    int paivita() {
        int laskettu = 0;
        std::vector<bool> muuttui(solmut_.size());
        for (std::size_t i = 0; i < solmut_.size(); ++i) {
            Solmu& s = solmut_[i];
            bool vanhempi_muuttui = s.vanhempi >= 0 && muuttui[s.vanhempi];
            if (!s.likainen && !vanhempi_muuttui) continue;
            Mat4 oma = matriisi(s.paikallinen);
            s.maailma = s.vanhempi >= 0 ? solmut_[s.vanhempi].maailma * oma
                                        : oma;
            s.likainen = false;
            muuttui[i] = true;
            ++laskettu;
        }
        return laskettu;
    }
    const Solmu& solmu(int i) const { return solmut_[i]; }
    Vec3 paikka(int i) const {
        return muunna_piste(solmut_[i].maailma, {0, 0, 0});
    }
    // @loppu puu

    // @alku kiinnita
    // Vaihtaa vanhemman niin, että solmu pysyy maailmassa paikallaan:
    // uusi paikallinen = (uuden vanhemman maailma)^-1 * oma maailma.
    // Uuden vanhemman on oltava taulukossa ennen solmua.
    void kiinnita(int i, int uusi_vanhempi) {
        Solmu& s = solmut_[i];
        Mat4 paikallinen = s.maailma;
        if (uusi_vanhempi >= 0)
            paikallinen = kaanteinen(solmut_[uusi_vanhempi].maailma) *
                          s.maailma;
        s.paikallinen = hajota(paikallinen);
        s.vanhempi = uusi_vanhempi;
        s.likainen = true;
    }
    // @loppu kiinnita

private:
    std::vector<Solmu> solmut_;
};

void piirra_nosturi(Piirtaja& p, const Nakymapuu& puu, int torni, int puomi,
                    int vaunu, int koukku, int kontti) {
    piirra(p, laatikkoverkko({-0.3, 0, -0.3}, {0.3, 6, 0.3}),
           puu.solmu(torni).maailma, {200, 170, 60});
    piirra(p, laatikkoverkko({-1.5, -0.15, -0.15}, {6, 0.15, 0.15}),
           puu.solmu(puomi).maailma, {200, 170, 60});
    piirra(p, laatikkoverkko({-0.3, -0.3, -0.3}, {0.3, 0, 0.3}),
           puu.solmu(vaunu).maailma, {70, 70, 80});
    p.viiva(puu.paikka(vaunu), puu.paikka(koukku), {30, 30, 30});
    piirra(p, laatikkoverkko({-0.6, -0.5, -0.6}, {0.6, 0.5, 0.6}),
           puu.solmu(kontti).maailma, {180, 80, 70});
}

int main(int argc, char** argv) {
    // @alku nosturi
    Nakymapuu puu;
    int alusta = puu.lisaa("alusta", -1, {});
    int torni = puu.lisaa("torni", alusta, {});
    int puomi = puu.lisaa("puomi", torni, {{0, 6, 0}, {}, {1, 1, 1}});
    int vaunu = puu.lisaa("vaunu", puomi, {{4, 0, 0}, {}, {1, 1, 1}});
    int koukku = puu.lisaa("koukku", vaunu, {{0, -5, 0}, {}, {1, 1, 1}});
    int kontti = puu.lisaa("kontti", -1, {{4, 0.5, 0}, {}, {1, 1, 1}});
    std::println("alussa laskettiin {} solmua", puu.paivita());
    std::println("  koukku {}  kontti {}", teksti(puu.paikka(koukku)),
                 teksti(puu.paikka(kontti)));
    // @loppu nosturi

    // Kuvitus: sama näkymä ennen tornin kääntöä ja sen jälkeen.
    auto tallenna = [&](const std::string& polku) {
        Kuva kuva(400, 300, {150, 185, 225});
        Piirtaja p(kuva, perspektiivi(1 / std::tan(rad(22)), 4.0 / 3, 0.1,
                                      100) *
                             katse({11, 8, 15}, {1, 3, -1}, {0, 1, 0}));
        piirra_lattia(p, 8, 1.0, {120, 150, 110}, {135, 165, 120});
        piirra_nosturi(p, puu, torni, puomi, vaunu, koukku, kontti);
        kuva.tallenna_ppm(polku);
    };

    // @alku nosto
    puu.kiinnita(kontti, koukku);  // kontti tarttuu koukkuun
    puu.muokkaa(koukku).sijainti.y = -3;  // nosto
    std::println("noston jälkeen laskettiin {} solmua", puu.paivita());
    std::println("  koukku {}  kontti {}", teksti(puu.paikka(koukku)),
                 teksti(puu.paikka(kontti)));
    // @loppu nosto
    if (argc > 1) tallenna(std::string(argv[1]) + "-1.ppm");

    // @alku kaanto
    puu.muokkaa(torni).kierto = akselikulma({0, 1, 0}, rad(90));
    std::println("tornin käännön jälkeen laskettiin {} solmua",
                 puu.paivita());
    std::println("  koukku {}  kontti {}", teksti(puu.paikka(koukku)),
                 teksti(puu.paikka(kontti)));
    if (argc > 1) tallenna(std::string(argv[1]) + "-2.ppm");
    puu.muokkaa(vaunu).sijainti.x = 2;
    std::println("vaunun siirron jälkeen laskettiin {} solmua",
                 puu.paivita());
    std::println("ilman muutoksia laskettiin {} solmua", puu.paivita());
    // @loppu kaanto

    // @alku irrotus
    puu.muokkaa(koukku).sijainti.y = -5;  // lasku
    puu.paivita();
    puu.kiinnita(kontti, -1);  // irti koukusta: jää maailmaan
    puu.muokkaa(koukku).sijainti.y = -2;
    puu.paivita();
    std::println("irrotuksen jälkeen");
    std::println("  koukku {}  kontti {}", teksti(puu.paikka(koukku)),
                 teksti(puu.paikka(kontti)));
    // @loppu irrotus

}
