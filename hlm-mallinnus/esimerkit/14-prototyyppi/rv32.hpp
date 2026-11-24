// RV32I-käskyjen koodaus ja pieni symbolinen kokoaja ohjelmille.
//
// Oikeassa virtuaaliprototyypissä ohjelma käännetään ristikääntäjällä
// (esim. riscv64-unknown-elf-gcc) ja ladataan ELF-tiedostosta. Tämä
// kokoaja tekee saman pienessä mittakaavassa ilman lisätyökaluja.
#pragma once
#include <cstdint>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace rv32 {

// @alku rekisterit
// ABI-nimet niille rekistereille, joita esimerkkiohjelma käyttää.
enum Rek : std::uint32_t {
    zero = 0, ra = 1, t0 = 5, t1 = 6, t2 = 7, s0 = 8, s1 = 9,
    a0 = 10, t3 = 28, t4 = 29
};
// @loppu rekisterit

// @alku koodaus
// Käskymuodot RISC-V:n käsikirjan mukaan.
constexpr std::uint32_t r_tyyppi(std::uint32_t f7, std::uint32_t rs2,
                                 std::uint32_t rs1, std::uint32_t f3,
                                 std::uint32_t rd, std::uint32_t op) {
    return f7 << 25 | rs2 << 20 | rs1 << 15 | f3 << 12 | rd << 7 | op;
}
constexpr std::uint32_t i_tyyppi(std::int32_t imm, std::uint32_t rs1,
                                 std::uint32_t f3, std::uint32_t rd,
                                 std::uint32_t op) {
    return (static_cast<std::uint32_t>(imm) & 0xFFF) << 20 | rs1 << 15 |
           f3 << 12 | rd << 7 | op;
}
constexpr std::uint32_t s_tyyppi(std::int32_t imm, std::uint32_t rs2,
                                 std::uint32_t rs1, std::uint32_t f3) {
    const auto u = static_cast<std::uint32_t>(imm);
    return (u >> 5 & 0x7F) << 25 | rs2 << 20 | rs1 << 15 | f3 << 12 |
           (u & 0x1F) << 7 | 0x23;
}
constexpr std::uint32_t b_tyyppi(std::int32_t imm, std::uint32_t rs2,
                                 std::uint32_t rs1, std::uint32_t f3) {
    const auto u = static_cast<std::uint32_t>(imm);
    return (u >> 12 & 1) << 31 | (u >> 5 & 0x3F) << 25 | rs2 << 20 |
           rs1 << 15 | f3 << 12 | (u >> 1 & 0xF) << 8 |
           (u >> 11 & 1) << 7 | 0x63;
}
constexpr std::uint32_t j_tyyppi(std::int32_t imm, std::uint32_t rd) {
    const auto u = static_cast<std::uint32_t>(imm);
    return (u >> 20 & 1) << 31 | (u >> 1 & 0x3FF) << 21 |
           (u >> 11 & 1) << 20 | (u >> 12 & 0xFF) << 12 | rd << 7 | 0x6F;
}
// @loppu koodaus

// @alku kokoaja
// Kerää käskyt ja datan tavuiksi. Nimiöihin voi viitata ennen niiden
// määrittelyä; viittaukset ratkaistaan funktiossa valmis().
class Kokoaja {
public:
    void nimio(const std::string& nimi) { nimiot_[nimi] = paikka(); }

    // Käskyt, joiden kaikki kentät tunnetaan heti. Operandit ovat
    // assemblyn järjestyksessä: lw rd, siirtymä(a) ja sw b, siirtymä(a).
    using I = std::int32_t;
    void lui(Rek rd, std::uint32_t y) { sana(y << 12 | rd << 7 | 0x37); }
    void addi(Rek rd, Rek a, I i) { sana(i_tyyppi(i, a, 0, rd, 0x13)); }
    void andi(Rek rd, Rek a, I i) { sana(i_tyyppi(i, a, 7, rd, 0x13)); }
    void add(Rek rd, Rek a, Rek b) { sana(r_tyyppi(0, b, a, 0, rd, 0x33)); }
    void srl(Rek rd, Rek a, Rek b) { sana(r_tyyppi(0, b, a, 5, rd, 0x33)); }
    void lw(Rek rd, I i, Rek a) { sana(i_tyyppi(i, a, 2, rd, 0x03)); }
    void lbu(Rek rd, I i, Rek a) { sana(i_tyyppi(i, a, 4, rd, 0x03)); }
    void sw(Rek b, I i, Rek a) { sana(s_tyyppi(i, b, a, 2)); }
    void jalr(Rek rd, I i, Rek a) { sana(i_tyyppi(i, a, 0, rd, 0x67)); }
    void ecall() { sana(0x73); }

    // Käskyt, joiden kohde on nimiö.
    void beq(Rek a, Rek b, const std::string& n) { haara(0, a, b, n); }
    void bne(Rek a, Rek b, const std::string& n) { haara(1, a, b, n); }
    void bge(Rek a, Rek b, const std::string& n) { haara(5, a, b, n); }
    void jal(Rek rd, const std::string& n) { viite(Viite::J, rd, n); }
    void la(Rek rd, const std::string& n) {  // lui + addi
        viite(Viite::LA, rd, n);
        sana(0);
    }

    // Data.
    void teksti(const std::string& s) {
        tavut_.insert(tavut_.end(), s.begin(), s.end());
        tavut_.push_back(0);
    }
    void tasaa() {
        while (tavut_.size() % 4 != 0) tavut_.push_back(0);
    }
    void data(std::uint32_t arvo) { sana(arvo); }

    std::vector<unsigned char> valmis();

private:
    enum class Viite { B, J, LA };
    struct Paikka {
        std::uint32_t osoite;
        Viite tyyppi;
        std::uint32_t f3, rs1, rs2;
        std::string nimi;
    };

    std::uint32_t paikka() const {
        return static_cast<std::uint32_t>(tavut_.size());
    }
    void sana(std::uint32_t s) {
        for (int i = 0; i < 4; ++i) tavut_.push_back(s >> (8 * i) & 0xFF);
    }
    void haara(std::uint32_t f3, Rek a, Rek b, const std::string& n) {
        viitteet_.push_back({paikka(), Viite::B, f3, a, b, n});
        sana(0);
    }
    void viite(Viite t, Rek rd, const std::string& n) {
        viitteet_.push_back({paikka(), t, 0, rd, 0, n});
        sana(0);
    }
    void kirjoita(std::uint32_t osoite, std::uint32_t s) {
        for (int i = 0; i < 4; ++i) tavut_[osoite + i] = s >> (8 * i) & 0xFF;
    }

    std::vector<unsigned char> tavut_;
    std::map<std::string, std::uint32_t> nimiot_;
    std::vector<Paikka> viitteet_;
};

inline std::vector<unsigned char> Kokoaja::valmis() {
    for (const Paikka& p : viitteet_) {
        const auto loytyi = nimiot_.find(p.nimi);
        if (loytyi == nimiot_.end()) {
            throw std::runtime_error("tuntematon nimiö " + p.nimi);
        }
        const std::uint32_t kohde = loytyi->second;
        const auto siirto = static_cast<std::int32_t>(kohde - p.osoite);
        switch (p.tyyppi) {
        case Viite::B:
            kirjoita(p.osoite, b_tyyppi(siirto, p.rs2, p.rs1, p.f3));
            break;
        case Viite::J:
            kirjoita(p.osoite, j_tyyppi(siirto, p.rs1));
            break;
        case Viite::LA: {  // addi on etumerkillinen: pyöristetään yläosa
            const std::uint32_t yla = (kohde + 0x800) >> 12;
            const auto ala = static_cast<std::int32_t>(kohde - (yla << 12));
            kirjoita(p.osoite, yla << 12 | p.rs1 << 7 | 0x37);
            kirjoita(p.osoite + 4, i_tyyppi(ala, p.rs1, 0, p.rs1, 0x13));
            break;
        }
        }
    }
    return tavut_;
}
// @loppu kokoaja

}  // namespace rv32
