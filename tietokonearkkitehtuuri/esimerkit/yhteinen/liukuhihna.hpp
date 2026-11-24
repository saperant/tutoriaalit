// Viisivaiheisen liukuhihnan (IF, ID, EX, MEM, WB) ajoitusmalli ja
// haarautumisen ennustimet. Malli on jälkiohjattu: käskytason
// simulaattori (kone.hpp) tuottaa oikean käskyjonon, ja tämä malli
// laskee, missä jaksossa kukin käsky olisi kunkin vaiheen läpi kulkenut.
//
// Yksinkertaistukset: haara ratkeaa EX-vaiheessa (väärän ennusteen hinta
// 2 jaksoa), jal-käskyn kohde tiedetään ID-vaiheessa (hinta 1 jakso),
// jalr ratkeaa EX-vaiheessa (2 jaksoa), oikein ennustettu hyppäävä haara
// ei maksa mitään (kohdepuskuri oletetaan), muisti vastaa aina yhdessä
// jaksossa ja kaikki laskutoimitukset, myös mul, vievät yhden EX-jakson.
#pragma once
#include <algorithm>
#include <cstdint>
#include <string>
#include <vector>

#include "kone.hpp"

namespace rv {

// @alku ennustimet
class Ennustin {
public:
    virtual ~Ennustin() = default;
    virtual std::string nimi() const = 0;
    virtual bool ennusta(u32 pc, u32 kohde) = 0;  // true = hypätään
    virtual void paivita(u32 pc, bool otettu) = 0;
};

class AinaEi final : public Ennustin {
public:
    std::string nimi() const override { return "aina ei"; }
    bool ennusta(u32, u32) override { return false; }
    void paivita(u32, bool) override {}
};

// Taaksepäin hyppäävät haarat ovat yleensä silmukoita: ennustetaan ne
// toteutuviksi ja eteenpäin hyppäävät toteutumattomiksi (BTFN).
class Taaksepain final : public Ennustin {
public:
    std::string nimi() const override { return "taaksepäin kyllä"; }
    bool ennusta(u32 pc, u32 kohde) override { return kohde < pc; }
    void paivita(u32, bool) override {}
};

// Taulukko kyllästyviä laskureita haaran osoitteen mukaan.
// Bittejä 1: muistetaan viimeisin suunta. Bittejä 2: laskuri 0..3,
// arvot 2 ja 3 ennustavat hypyn, joten yksi poikkeus ei käännä ennustetta.
class Laskuri final : public Ennustin {
public:
    Laskuri(int bitteja, std::size_t koko)
        : bitteja_(bitteja), tilat_(koko, 0) {}
    std::string nimi() const override {
        return std::format("{}-bittinen ({})", bitteja_, tilat_.size());
    }
    bool ennusta(u32 pc, u32) override {
        return tilat_[indeksi(pc)] >= (1 << (bitteja_ - 1));
    }
    void paivita(u32 pc, bool otettu) override {
        auto& t = tilat_[indeksi(pc)];
        const int ylin = (1 << bitteja_) - 1;
        t = static_cast<std::uint8_t>(
            otettu ? std::min(t + 1, ylin) : std::max(t - 1, 0));
    }

private:
    std::size_t indeksi(u32 pc) const { return (pc >> 2) % tilat_.size(); }
    int bitteja_;
    std::vector<std::uint8_t> tilat_;
};
// @loppu ennustimet

struct Asetukset {
    bool eteenpainkytkenta = true;
    Ennustin* ennustin = nullptr;  // nullptr: ennustetaan "ei hypätä"
};

struct Tulos {
    std::uint64_t kaskyt = 0, syklit = 0;
    std::uint64_t datapysahdykset = 0, ohjauspysahdykset = 0;
    std::uint64_t haarat = 0, vaarat = 0;  // väärin ennustetut haarat
    double cpi() const {
        return static_cast<double>(syklit) / static_cast<double>(kaskyt);
    }
    double tarkkuus() const {
        return haarat == 0 ? 1.0
                           : 1.0 - static_cast<double>(vaarat) /
                                       static_cast<double>(haarat);
    }
};

struct Vaiheet {  // jaksot, joissa käsky oli vaiheissa IF ja EX
    long long nouto, ex;
};

// @alku malli
inline Tulos simuloi(const std::vector<Tapahtuma>& jalki,
                     const Asetukset& a,
                     std::vector<Vaiheet>* kaavio = nullptr) {
    struct Tuottaja { long long ex = -100, mem = -100, wb = -100;
                      bool lataus = false; };
    std::array<Tuottaja, 32> rekisterit{};
    Tulos t;
    long long ex_ed = 1, nouto_ed = -1;  // ensimmäinen EX jaksossa 2
    int hinta = 0;                        // edellisen käskyn ohjaushinta
    for (const Tapahtuma& k : jalki) {
        const long long nouto =
            hinta > 0 ? ex_ed - 1 + hinta : nouto_ed + 1;
        long long ex = std::max(nouto + 2, ex_ed + 1);
        const long long ilman_dataa = ex;
        // Operandin on oltava valmis: eteenpäinkytkennällä EX-vaiheen
        // tulos seuraavaan EX:ään ja latauksen tulos MEM:n jälkeen,
        // ilman sitä vasta rekisteritiedoston kautta (WB, sitten ID).
        auto odota = [&](bool lukee, u32 r) {
            if (!lukee || r == 0) return;
            const Tuottaja& p = rekisterit[r];
            const long long valmis =
                a.eteenpainkytkenta ? (p.lataus ? p.mem : p.ex) + 1
                                    : p.wb + 1;
            ex = std::max(ex, valmis);
        };
        odota(k.lukee_rs1, k.f.rs1);
        odota(k.lukee_rs2, k.f.rs2);
        t.datapysahdykset += static_cast<std::uint64_t>(ex - ilman_dataa);
        if (k.kirjoittaa_rd)
            rekisterit[k.f.rd] = {ex, ex + 1, ex + 2, k.lataus};
        // Ohjausriippuvuudet: väärä polku täytyy hylätä.
        hinta = 0;
        if (k.haara) {
            ++t.haarat;
            const u32 kohde = k.pc + static_cast<u32>(k.f.imm);
            const bool ennuste =
                a.ennustin && a.ennustin->ennusta(k.pc, kohde);
            if (a.ennustin) a.ennustin->paivita(k.pc, k.otettu);
            if (ennuste != k.otettu) { ++t.vaarat; hinta = 2; }
        } else if (k.hyppy) {
            hinta = k.f.opcode == 0x6f ? 1 : 2;  // jal / jalr
        }
        t.ohjauspysahdykset += static_cast<std::uint64_t>(hinta);
        if (kaavio) kaavio->push_back({nouto, ex});
        ex_ed = ex;
        nouto_ed = nouto;
        ++t.kaskyt;
    }
    t.syklit = static_cast<std::uint64_t>(ex_ed + 3);  // MEM, WB, 0-alku
    return t;
}
// @loppu malli

// Liukuhihnakaavio: rivi käskyä kohti, sarake jaksoa kohti.
// ** = käsky odottaa: ennen ID:tä noutovaiheessa (edellinen käsky
// on vielä ID:ssä), ID:n jälkeen dekoodausvaiheessa (operandi ei ole
// vielä valmis).
inline std::string piirra(const std::vector<Tapahtuma>& jalki,
                          const std::vector<Vaiheet>& vaiheet,
                          std::size_t rivit) {
    std::string s;
    rivit = std::min(rivit, jalki.size());
    for (std::size_t i = 0; i < rivit; ++i) {
        const auto [nouto, ex] = vaiheet[i];
        // ID:hen päästään, kun edellinen käsky on siirtynyt EX:ään.
        const long long id =
            i == 0 ? nouto + 1 : std::max(nouto + 1, vaiheet[i - 1].ex);
        std::string rivi = std::format("{:<20}",
                                       pura_teksti(jalki[i].kasky,
                                                   jalki[i].pc));
        for (long long c = 0; c <= ex + 2; ++c) {
            if (c < nouto) rivi += "   ";
            else if (c == nouto) rivi += "IF ";
            else if (c == id) rivi += "ID ";
            else if (c < ex) rivi += "** ";
            else if (c == ex) rivi += "EX ";
            else if (c == ex + 1) rivi += "ME ";
            else rivi += "WB";
        }
        s += rivi + "\n";
    }
    return s;
}

}  // namespace rv
