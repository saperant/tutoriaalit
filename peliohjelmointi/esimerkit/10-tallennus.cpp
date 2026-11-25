// Pelitilanteen tallennus: tila kirjoitetaan tavuiksi kenttä kerrallaan,
// ja otsakkeessa on tunniste, versio ja tarkistussumma. Lataus hylkää
// vioittuneen tiedoston ja osaa lukea myös vanhan version.
#include <cstdint>
#include <expected>
#include <print>
#include <span>
#include <string_view>
#include <vector>

using Tavut = std::vector<std::uint8_t>;

// @alku tila
struct Tilanne {
    std::uint32_t taso = 1;
    std::uint32_t pisteet = 0;
    std::int32_t x = 0, y = 0;   // pelaajan ruutu
    std::uint32_t avaimet = 0;   // lisätty versiossa 2
};

constexpr std::uint32_t TUNNISTE = 0x4C4C4154;  // "TALL"
constexpr std::uint32_t VERSIO = 2;
// @loppu tila

// @alku tavut
// Kentät kirjoitetaan yksitellen pienin tavu ensin. Koko rakenteen
// kopiointi muistista sitoisi tiedoston kääntäjän täytetavuihin ja
// prosessorin tavujärjestykseen.
void kirjoita(Tavut& t, std::uint32_t arvo) {
    for (int i = 0; i < 4; ++i) {
        t.push_back(static_cast<std::uint8_t>(arvo >> (8 * i)));
    }
}

struct Lukija {
    std::span<const std::uint8_t> data;
    bool virhe = false;

    std::uint32_t u32() {
        if (data.size() < 4) {
            virhe = true;  // tiedosto loppui kesken
            return 0;
        }
        std::uint32_t arvo = 0;
        for (int i = 0; i < 4; ++i) {
            const auto tavu = data[static_cast<std::size_t>(i)];
            arvo |= static_cast<std::uint32_t>(tavu) << (8 * i);
        }
        data = data.subspan(4);
        return arvo;
    }
};

// FNV-1a: yksinkertainen tarkistussumma vahinkojen havaitsemiseen.
std::uint32_t summa(std::span<const std::uint8_t> data) {
    std::uint32_t h = 2166136261u;
    for (std::uint8_t tavu : data) {
        h = (h ^ tavu) * 16777619u;
    }
    return h;
}
// @loppu tavut

// @alku tallenna
Tavut tallenna(const Tilanne& t) {
    Tavut sisalto;
    kirjoita(sisalto, t.taso);
    kirjoita(sisalto, t.pisteet);
    kirjoita(sisalto, static_cast<std::uint32_t>(t.x));
    kirjoita(sisalto, static_cast<std::uint32_t>(t.y));
    kirjoita(sisalto, t.avaimet);

    Tavut tiedosto;
    kirjoita(tiedosto, TUNNISTE);
    kirjoita(tiedosto, VERSIO);
    kirjoita(tiedosto, static_cast<std::uint32_t>(sisalto.size()));
    kirjoita(tiedosto, summa(sisalto));
    tiedosto.insert(tiedosto.end(), sisalto.begin(), sisalto.end());
    return tiedosto;
}
// @loppu tallenna

// @alku lataa
std::expected<Tilanne, std::string_view> lataa(const Tavut& tiedosto) {
    Lukija otsake{tiedosto};
    const std::uint32_t tunniste = otsake.u32(), versio = otsake.u32();
    const std::uint32_t pituus = otsake.u32(), tarkiste = otsake.u32();
    if (otsake.virhe || tunniste != TUNNISTE) {
        return std::unexpected("ei ole tallennustiedosto");
    }
    if (versio == 0 || versio > VERSIO) {
        return std::unexpected("tuntematon versio");
    }
    if (otsake.data.size() != pituus) {
        return std::unexpected("tiedosto on katkennut");
    }
    if (summa(otsake.data) != tarkiste) {
        return std::unexpected("tarkistussumma ei täsmää");
    }
    Lukija l{otsake.data};
    Tilanne t;
    t.taso = l.u32();
    t.pisteet = l.u32();
    t.x = static_cast<std::int32_t>(l.u32());
    t.y = static_cast<std::int32_t>(l.u32());
    if (versio >= 2) {
        t.avaimet = l.u32();  // versiossa 1 kenttää ei ole: oletus 0
    }
    if (l.virhe || !l.data.empty()) {
        return std::unexpected("sisältö ei vastaa versiota");
    }
    return t;
}
// @loppu lataa

void nayta(std::string_view nimi, const Tavut& tiedosto) {
    if (const auto t = lataa(tiedosto)) {
        std::println("{:18} taso {}, pisteet {}, paikka ({}, {}), "
                     "avaimia {}", nimi, t->taso, t->pisteet, t->x, t->y,
                     t->avaimet);
    } else {
        std::println("{:18} hylätty: {}", nimi, t.error());
    }
}

int main() {
    const Tilanne peli{3, 1250, 17, -4, 2};
    const Tavut ehja = tallenna(peli);
    std::println("tiedoston koko {} tavua", ehja.size());
    nayta("ehjä", ehja);

    Tavut vioittunut = ehja;
    vioittunut[21] ^= 0x01;  // yksi bitti pisteissä kääntyy
    nayta("yksi bitti vaihtui", vioittunut);

    const Tavut katkennut(ehja.begin(), ehja.end() - 6);
    nayta("katkennut", katkennut);

    // Vanhan version tiedosto: sama rakenne ilman avaimia.
    Tavut sisalto;
    for (std::uint32_t arvo : {2u, 400u, 5u, 9u}) {
        kirjoita(sisalto, arvo);
    }
    Tavut vanha;
    for (std::uint32_t arvo :
         {TUNNISTE, 1u, static_cast<std::uint32_t>(sisalto.size()),
          summa(sisalto)}) {
        kirjoita(vanha, arvo);
    }
    vanha.insert(vanha.end(), sisalto.begin(), sisalto.end());
    nayta("versio 1", vanha);

    Tavut uudempi = ehja;
    uudempi[4] = 3;  // versio, jota tämä ohjelma ei tunne
    nayta("versio 3", uudempi);
}
