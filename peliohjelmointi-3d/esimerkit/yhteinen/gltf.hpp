// glTF 2.0 -tiedoston lataus pelin omiin rakenteisiin: solmut, verkot,
// ihot ja animaatiot. JSON jäsennetään kirjastolla nlohmann/json;
// binääridata luetaan itse ja jokainen viittaus tarkistetaan.
#pragma once
#include "luuranko.hpp"
#include "mallit.hpp"

#include <nlohmann/json.hpp>

#include <cstring>
#include <expected>
#include <filesystem>
#include <fstream>
#include <map>
#include <stdexcept>

// @alku rakenteet
struct GltfSolmu {
    std::string nimi;
    int vanhempi = -1;
    Muunnos paikallinen;
    int verkko = -1, iho = -1;  // indeksit tai -1
};
struct GltfVerkko {
    std::string nimi;
    Verkko verkko;
    std::vector<Painot> painot;  // tyhjä, jos verkkoa ei ole sidottu
    Vari vari{200, 200, 200};
};
struct GltfIho {
    std::vector<int> nivelet;      // solmujen indeksit
    std::vector<Mat4> kaanteiset;  // käänteiset sidontamatriisit
};
struct Gltf {
    std::vector<GltfSolmu> solmut;
    std::vector<GltfVerkko> verkot;
    std::vector<GltfIho> ihot;
    std::vector<Leike> animaatiot;  // kanavan nivel on solmun indeksi
};
// @loppu rakenteet

namespace gltf_apu {
using Json = nlohmann::json;

// @alku lukija
// Accessor on tyypitetty näkymä binääripuskuriin. Lukija tarkistaa
// tyypin ja sen, ettei mikään luku osu puskurin ulkopuolelle.
struct Taulukko {
    int leveys = 1;             // komponentteja alkiota kohden
    std::vector<double> arvot;  // alkiot peräkkäin
    std::size_t maara() const { return arvot.size() / leveys; }
    double operator()(std::size_t alkio, int k) const {
        return arvot[alkio * leveys + k];
    }
};

class Lukija {
public:
    Lukija(const Json& j, const std::filesystem::path& hakemisto) : j_(j) {
        for (const Json& b : j.at("buffers")) {
            std::string uri = b.at("uri");
            if (uri.starts_with("data:"))
                throw std::runtime_error("upotettua dataa ei tueta");
            std::ifstream f(hakemisto / uri, std::ios::binary);
            if (!f) throw std::runtime_error("puskuri puuttuu: " + uri);
            puskurit_.emplace_back(std::istreambuf_iterator<char>(f),
                                   std::istreambuf_iterator<char>());
        }
    }

    Taulukko lue(int indeksi, const std::string& tyyppi) const {
        const Json& a = j_.at("accessors").at(indeksi);
        const Json& nakyma =
            j_.at("bufferViews").at(a.at("bufferView").get<std::size_t>());
        if (a.at("type") != tyyppi)
            throw std::runtime_error(std::format(
                "accessor {}: odotettiin tyyppiä {}", indeksi, tyyppi));
        if (nakyma.contains("byteStride"))
            throw std::runtime_error("lomitettua dataa ei tueta");
        static const std::map<std::string, int> leveydet = {
            {"SCALAR", 1}, {"VEC3", 3}, {"VEC4", 4}, {"MAT4", 16}};
        static const std::map<int, std::size_t> koot = {
            {5121, 1}, {5123, 2}, {5125, 4}, {5126, 4}};
        int komponentti = a.at("componentType");
        if (!koot.contains(komponentti))
            throw std::runtime_error("tuntematon komponenttityyppi");
        Taulukko t{leveydet.at(tyyppi), {}};
        std::size_t koko = koot.at(komponentti), maara = a.at("count");
        std::size_t alku = nakyma.value("byteOffset", std::size_t{0}) +
                           a.value("byteOffset", std::size_t{0});
        const auto& puskuri =
            puskurit_.at(nakyma.at("buffer").get<std::size_t>());
        if (alku + maara * t.leveys * koko > puskuri.size())
            throw std::runtime_error(std::format(
                "accessor {} lukee puskurin ohi ({} > {} tavua)", indeksi,
                alku + maara * t.leveys * koko, puskuri.size()));
        for (std::size_t i = 0; i < maara * t.leveys; ++i) {
            const char* p = puskuri.data() + alku + i * koko;
            if (komponentti == 5126) {  // 32-bittinen liukuluku
                float f;
                std::memcpy(&f, p, 4);
                t.arvot.push_back(f);
            } else {  // etumerkitön kokonaisluku, pienin tavu ensin
                std::uint32_t u = 0;
                std::memcpy(&u, p, koko);
                t.arvot.push_back(u);
            }
        }
        return t;
    }

private:
    const Json& j_;
    std::vector<std::vector<char>> puskurit_;
};
// @loppu lukija

// @alku solmut
inline std::vector<GltfSolmu> solmut(const Json& j) {
    std::vector<GltfSolmu> tulos;
    for (const Json& n : j.at("nodes")) {
        GltfSolmu s;
        s.nimi = n.value("name", "");
        s.verkko = n.value("mesh", -1);
        s.iho = n.value("skin", -1);
        if (n.contains("matrix")) {  // 16 lukua sarakkeittain
            Mat4 m;
            for (int i = 0; i < 16; ++i) m.m[i % 4][i / 4] = n["matrix"][i];
            s.paikallinen = hajota(m);
        }
        if (n.contains("translation")) {
            const Json& t = n["translation"];
            s.paikallinen.sijainti = {t[0], t[1], t[2]};
        }
        if (n.contains("rotation")) {  // tiedostossa järjestys x, y, z, w
            const Json& r = n["rotation"];
            s.paikallinen.kierto = {r[3], r[0], r[1], r[2]};
        }
        if (n.contains("scale")) {
            const Json& k = n["scale"];
            s.paikallinen.skaala = {k[0], k[1], k[2]};
        }
        tulos.push_back(s);
    }
    // Vanhempi päätellään lapsiluetteloista.
    for (std::size_t i = 0; i < tulos.size(); ++i)
        if (j["nodes"][i].contains("children"))
            for (int lapsi : j["nodes"][i]["children"])
                tulos.at(lapsi).vanhempi = static_cast<int>(i);
    return tulos;
}
// @loppu solmut

// @alku verkot
inline std::vector<GltfVerkko> verkot(const Json& j, const Lukija& lukija) {
    std::vector<GltfVerkko> tulos;
    if (!j.contains("meshes")) return tulos;
    for (const Json& m : j["meshes"]) {
        const Json& osa = m.at("primitives").at(0);  // vain ensimmäinen osa
        const Json& attr = osa.at("attributes");
        GltfVerkko v;
        v.nimi = m.value("name", "");
        Taulukko paikat = lukija.lue(attr.at("POSITION"), "VEC3");
        for (std::size_t i = 0; i < paikat.maara(); ++i)
            v.verkko.pisteet.push_back(
                {paikat(i, 0), paikat(i, 1), paikat(i, 2)});
        Taulukko ind = lukija.lue(osa.at("indices"), "SCALAR");
        for (std::size_t i = 0; i + 2 < ind.maara(); i += 3) {
            std::array<int, 3> k{};
            for (int n = 0; n < 3; ++n) {
                k[n] = static_cast<int>(ind(i + n, 0));
                if (k[n] >= static_cast<int>(paikat.maara()))
                    throw std::runtime_error("indeksi osoittaa verkon ohi");
            }
            v.verkko.kolmiot.push_back(k);
        }
        if (attr.contains("JOINTS_0")) {
            Taulukko n = lukija.lue(attr["JOINTS_0"], "VEC4");
            Taulukko w = lukija.lue(attr.at("WEIGHTS_0"), "VEC4");
            for (std::size_t i = 0; i < n.maara(); ++i) {
                Painot p;
                for (int k = 0; k < 4; ++k) {
                    p.nivel[k] = static_cast<int>(n(i, k));
                    p.paino[k] = w(i, k);
                }
                v.painot.push_back(p);
            }
        }
        if (osa.contains("material")) {
            const Json& vari = j.at("materials")
                                   .at(osa["material"].get<std::size_t>())
                                   .at("pbrMetallicRoughness")
                                   .at("baseColorFactor");
            auto tavu = [&vari](int i) {
                return static_cast<std::uint8_t>(vari[i].get<double>() *
                                                 255);
            };
            v.vari = {tavu(0), tavu(1), tavu(2)};
        }
        tulos.push_back(v);
    }
    return tulos;
}
// @loppu verkot

// @alku animaatiot
inline std::vector<Leike> animaatiot(const Json& j, const Lukija& lukija) {
    std::vector<Leike> tulos;
    if (!j.contains("animations")) return tulos;
    for (const Json& a : j["animations"]) {
        Leike leike;
        leike.nimi = a.value("name", "");
        for (const Json& kanava : a.at("channels")) {
            const Json& nayte = a.at("samplers").at(
                kanava.at("sampler").get<std::size_t>());
            if (nayte.value("interpolation", "LINEAR") != "LINEAR")
                throw std::runtime_error("vain LINEAR-interpolointi");
            Kanava k;
            k.nivel = kanava.at("target").at("node");
            std::string polku = kanava["target"].at("path");
            Taulukko ajat = lukija.lue(nayte.at("input"), "SCALAR");
            k.ajat = ajat.arvot;
            leike.kesto = std::max(leike.kesto, k.ajat.back());
            if (polku == "rotation") {
                k.kohde = Kanava::Kohde::Kierto;
                Taulukko q = lukija.lue(nayte.at("output"), "VEC4");
                for (std::size_t i = 0; i < q.maara(); ++i)
                    k.kierrot.push_back(
                        normalisoi(Kvat{q(i, 3), q(i, 0), q(i, 1), q(i, 2)}));
            } else if (polku == "translation" || polku == "scale") {
                k.kohde = polku == "scale" ? Kanava::Kohde::Skaala
                                           : Kanava::Kohde::Siirto;
                Taulukko v = lukija.lue(nayte.at("output"), "VEC3");
                for (std::size_t i = 0; i < v.maara(); ++i)
                    k.vektorit.push_back({v(i, 0), v(i, 1), v(i, 2)});
            } else {
                throw std::runtime_error("tuntematon animaatiokohde");
            }
            leike.kanavat.push_back(k);
        }
        tulos.push_back(leike);
    }
    return tulos;
}
// @loppu animaatiot
}  // namespace gltf_apu

// @alku lataa
// Lataa tiedoston tai palauttaa virheilmoituksen. Rikkinäinen tiedosto
// ei saa kaataa peliä: kaikki jäsennyksen ja tarkistusten poikkeukset
// muutetaan tässä virhearvoksi.
inline std::expected<Gltf, std::string> lataa_gltf(
    const std::filesystem::path& polku) {
    try {
        std::ifstream f(polku);
        if (!f) return std::unexpected("tiedosto puuttuu");
        gltf_apu::Json j = gltf_apu::Json::parse(f);
        if (j.at("asset").at("version") != "2.0")
            return std::unexpected("vain glTF 2.0 on tuettu");
        gltf_apu::Lukija lukija(j, polku.parent_path());
        Gltf g;
        g.solmut = gltf_apu::solmut(j);
        g.verkot = gltf_apu::verkot(j, lukija);
        g.animaatiot = gltf_apu::animaatiot(j, lukija);
        if (j.contains("skins"))
            for (const auto& s : j["skins"]) {
                GltfIho iho;
                iho.nivelet = s.at("joints").get<std::vector<int>>();
                auto m = lukija.lue(s.at("inverseBindMatrices"), "MAT4");
                for (std::size_t i = 0; i < m.maara(); ++i) {
                    Mat4 k;  // tiedostossa sarakkeittain
                    for (int n = 0; n < 16; ++n) k.m[n % 4][n / 4] = m(i, n);
                    iho.kaanteiset.push_back(k);
                }
                g.ihot.push_back(iho);
            }
        return g;
    } catch (const std::exception& e) {
        return std::unexpected(std::string(e.what()));
    }
}
// @loppu lataa

// @alku maailmat
// Solmujen maailmamatriisit. glTF ei takaa, että vanhempi on taulukossa
// ennen lasta, joten matriisi lasketaan vanhempia pitkin tarvittaessa.
inline std::vector<Mat4> maailmamatriisit(const Gltf& g) {
    std::vector<Mat4> m(g.solmut.size());
    std::vector<bool> valmis(g.solmut.size());
    auto laske = [&](auto& itse, int i) -> const Mat4& {
        if (!valmis[i]) {
            const GltfSolmu& s = g.solmut[i];
            m[i] = s.vanhempi >= 0
                       ? itse(itse, s.vanhempi) * matriisi(s.paikallinen)
                       : matriisi(s.paikallinen);
            valmis[i] = true;
        }
        return m[i];
    };
    for (std::size_t i = 0; i < m.size(); ++i)
        laske(laske, static_cast<int>(i));
    return m;
}
// @loppu maailmat

// @alku luurangoksi
// Ihon nivelet pelin luurangoksi. Nivelet numeroidaan ihon järjestyksessä,
// ja animaatioiden kanavat osoitetaan samoihin numeroihin.
struct Animoitu {
    Luuranko luuranko;
    std::vector<Leike> leikkeet;
};
inline std::expected<Animoitu, std::string> luurangoksi(const Gltf& g,
                                                        int iho) {
    const GltfIho& i = g.ihot.at(iho);
    std::map<int, int> nivel_solmusta;
    Animoitu a;
    for (std::size_t k = 0; k < i.nivelet.size(); ++k) {
        const GltfSolmu& s = g.solmut.at(i.nivelet[k]);
        int vanhempi = nivel_solmusta.contains(s.vanhempi)
                           ? nivel_solmusta[s.vanhempi]
                           : -1;
        if (s.vanhempi >= 0 && vanhempi < 0 && k > 0)
            return std::unexpected("nivelen vanhempi ei ole ennen lasta");
        a.luuranko.nivelet.push_back(
            {s.nimi, vanhempi, s.paikallinen, i.kaanteiset.at(k)});
        nivel_solmusta[i.nivelet[k]] = static_cast<int>(k);
    }
    for (Leike leike : g.animaatiot) {
        std::erase_if(leike.kanavat, [&](const Kanava& k) {
            return !nivel_solmusta.contains(k.nivel);
        });
        for (Kanava& k : leike.kanavat) k.nivel = nivel_solmusta[k.nivel];
        a.leikkeet.push_back(leike);
    }
    return a;
}
// @loppu luurangoksi

// Esimerkkien resurssihakemisto lähdekoodin vieressä. Oikea peli etsii
// resurssinsa asennushakemistosta, ei käännösaikaisesta polusta.
inline std::filesystem::path resurssi(const std::string& nimi) {
    return std::filesystem::path(__FILE__).parent_path().parent_path() /
           "resurssit" / nimi;
}
