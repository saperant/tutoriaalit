// Käskytason RV32I-simulaattori (ISS). Suorittaa ohjelman käsky
// kerrallaan ja palauttaa jokaisesta käskystä tapahtuman, jota
// liukuhihna- ja välimuistimallit käyttävät syötteenään.
//
// Muisti: 64 KiB osoitteesta 0. Pino alkaa muistin lopusta.
// Järjestelmäkutsut (ecall, kun ansat on pois päältä): a7 = 1 tulostaa
// kokonaisluvun a0, 11 merkin a0 ja 10 lopettaa ohjelman.
// Muistiinkuvattu I/O: UART 0x1000'0000 (kirjoitus = merkki),
// ajastin mtime 0x0200'bff8 ja vertailuarvo mtimecmp 0x0200'4000.
#pragma once
#include <cstdint>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

#include "rv32i.hpp"

namespace rv {

// @alku tapahtuma
// Yksi suoritettu käsky: mitä luettiin, kirjoitettiin ja mihin hypättiin.
struct Tapahtuma {
    u32 pc = 0, kasky = 0;
    Kentat f{};
    bool kirjoittaa_rd = false;           // tulos rekisteriin rd != x0
    bool lukee_rs1 = false, lukee_rs2 = false;
    bool lataus = false, talletus = false;
    u32 osoite = 0;                       // datamuistin osoite
    bool haara = false, hyppy = false;    // beq…/jal, jalr
    bool otettu = false;                  // haara toteutui
    u32 seuraava = 0;                     // seuraavan käskyn osoite
};
// @loppu tapahtuma

class Kone {
public:
    static constexpr u32 MUISTI = 64 * 1024;
    static constexpr u32 UART = 0x1000'0000;
    static constexpr u32 MTIME = 0x0200'bff8;
    static constexpr u32 MTIMECMP = 0x0200'4000;

    std::array<u32, 32> x{};
    u32 pc = 0;
    std::vector<std::uint8_t> muisti = std::vector<std::uint8_t>(MUISTI);
    std::string tuloste;
    bool pysahtynyt = false;
    std::map<u32, u32> csr;
    bool ansat = false;  // true: ecall ja virheet ohjataan mtvec:iin
    std::uint64_t suoritetut = 0;
    std::uint64_t mtimecmp = ~std::uint64_t{0};

    explicit Kone(const Ohjelma& o) {
        if (o.kuva.size() > MUISTI) throw std::runtime_error("liian iso");
        std::copy(o.kuva.begin(), o.kuva.end(), muisti.begin());
        x[2] = MUISTI;  // sp
    }

    u32 lue(u32 a, int tavuja) const {
        if (a == MTIME) return static_cast<u32>(suoritetut);
        if (a == MTIMECMP) return static_cast<u32>(mtimecmp);
        tarkista(a, tavuja);
        u32 v = 0;
        for (int i = tavuja - 1; i >= 0; --i)
            v = v << 8 | muisti[a + static_cast<u32>(i)];
        return v;
    }

    void kirjoita(u32 a, u32 v, int tavuja) {
        if (a == UART) { tuloste += static_cast<char>(v); return; }
        if (a == MTIMECMP) { mtimecmp = v; return; }
        tarkista(a, tavuja);
        for (int i = 0; i < tavuja; ++i)
            muisti[a + static_cast<u32>(i)] =
                static_cast<std::uint8_t>(v >> (8 * i));
    }

    // @alku ansa
    // Ansa: tallennetaan paluuosoite ja syy, hypätään käsittelijään.
    void ansa(u32 syy, u32 paluu) {
        if (!ansat)
            throw std::runtime_error(std::format("ansa {} kohdassa 0x{:x}",
                                                 syy, paluu));
        csr[0x341] = paluu;                           // mepc
        csr[0x342] = syy;                             // mcause
        const u32 ms = csr[0x300];                    // mstatus
        csr[0x300] = (ms & ~0x88u) | (ms & 0x8u) << 4;  // MPIE = MIE
        pc = csr[0x305];                              // mtvec
    }
    // @loppu ansa

    Tapahtuma askel();

    std::vector<Tapahtuma> aja(std::uint64_t enintaan = 50'000'000) {
        std::vector<Tapahtuma> jalki;
        while (!pysahtynyt && suoritetut < enintaan)
            jalki.push_back(askel());
        if (!pysahtynyt) throw std::runtime_error("ohjelma ei päättynyt");
        return jalki;
    }

private:
    void tarkista(u32 a, int tavuja) const {
        if (a > MUISTI - static_cast<u32>(tavuja))
            throw std::runtime_error(std::format("osoite 0x{:x}", a));
    }
};

inline Tapahtuma Kone::askel() {
    // Ajastinkeskeytys, jos se on sallittu (mstatus.MIE, mie.MTIE).
    if (suoritetut >= mtimecmp && (csr[0x300] & 0x8) &&
        (csr[0x304] & 0x80)) {
        ansa(0x8000'0007, pc);
    }
    const u32 k = lue(pc, 4);
    Tapahtuma t{.pc = pc, .kasky = k, .f = pura(k)};
    const Kentat& f = t.f;
    const u32 a = x[f.rs1], b = x[f.rs2];
    const u32 imm = static_cast<u32>(f.imm);
    u32 seuraava = pc + 4;
    u32 tulos = 0;
    t.lukee_rs1 = f.muoto != Muoto::U && f.muoto != Muoto::J;
    t.lukee_rs2 = f.muoto == Muoto::R || f.muoto == Muoto::S ||
                  f.muoto == Muoto::B;
    t.kirjoittaa_rd = f.muoto != Muoto::S && f.muoto != Muoto::B &&
                      f.rd != 0;
    auto sa = [](u32 v) { return static_cast<i32>(v); };
    switch (f.opcode) {
    case 0x37: tulos = imm; break;
    case 0x17: tulos = pc + imm; break;
    case 0x6f: tulos = pc + 4; seuraava = pc + imm; t.hyppy = true; break;
    case 0x67:
        tulos = pc + 4;
        seuraava = (a + imm) & ~1u;
        t.hyppy = true;
        break;
    case 0x63: {
        const bool ehto[8] = {a == b,         a != b,  false, false,
                              sa(a) < sa(b),  sa(a) >= sa(b),
                              a < b,          a >= b};
        t.haara = true;
        t.otettu = ehto[f.funct3];
        if (t.otettu) seuraava = pc + imm;
        break;
    }
    case 0x03: {
        t.lataus = true;
        t.osoite = a + imm;
        const int koko = 1 << (f.funct3 & 3);
        if (t.osoite % static_cast<u32>(koko) != 0) {
            t.kirjoittaa_rd = false;
            ansa(4, pc);  // kohdistamaton lataus
            ++suoritetut;
            t.seuraava = this->pc;
            return t;
        }
        tulos = lue(t.osoite, koko);
        if (f.funct3 == 0) tulos = static_cast<u32>(laajenna(tulos, 8));
        if (f.funct3 == 1) tulos = static_cast<u32>(laajenna(tulos, 16));
        break;
    }
    case 0x23:
        t.talletus = true;
        t.osoite = a + imm;
        kirjoita(t.osoite, b, 1 << f.funct3);
        break;
    case 0x13:
    case 0x33: {
        const bool r = f.opcode == 0x33;
        const u32 c = r ? b : imm;
        const u32 siirto = c & 0x1f;
        const bool vaihto = f.funct7 == 0x20;
        if (r && f.funct7 == 1) { tulos = a * b; break; }  // mul
        switch (f.funct3) {
        case 0: tulos = r && vaihto ? a - c : a + c; break;
        case 1: tulos = a << siirto; break;
        case 2: tulos = sa(a) < sa(c); break;
        case 3: tulos = a < c; break;
        case 4: tulos = a ^ c; break;
        case 5: tulos = vaihto ? static_cast<u32>(sa(a) >> siirto)
                               : a >> siirto; break;
        case 6: tulos = a | c; break;
        case 7: tulos = a & c; break;
        }
        break;
    }
    case 0x73:
        if (f.funct3 == 0) {
            t.kirjoittaa_rd = false;
            // @alku mret
            if (f.imm == 0x302) {  // mret: MIE = MPIE, pc = mepc
                const u32 ms = csr[0x300];
                csr[0x300] = (ms & ~0x8u) | (ms >> 4 & 0x8u);
                seuraava = csr[0x341];
                // @loppu mret
            } else if (ansat) {
                ansa(11, pc);  // ecall koneen tilassa
                ++suoritetut;
                t.seuraava = this->pc;
                return t;
            } else if (x[17] == 1) {
                tuloste += std::to_string(sa(x[10]));
            } else if (x[17] == 11) {
                tuloste += static_cast<char>(x[10]);
            } else if (x[17] == 10) {
                pysahtynyt = true;
            }
        } else {  // csrrw, csrrs
            const u32 nro = imm & 0xfff;
            tulos = csr[nro];
            if (f.funct3 == 1) csr[nro] = a;
            else if (f.rs1 != 0) csr[nro] |= a;
        }
        break;
    default:
        t.kirjoittaa_rd = false;
        ansa(2, pc);  // laiton käsky
        ++suoritetut;
        t.seuraava = this->pc;
        return t;
    }
    if (t.kirjoittaa_rd) x[f.rd] = tulos;
    x[0] = 0;
    pc = seuraava;
    t.seuraava = seuraava;
    ++suoritetut;
    return t;
}

}  // namespace rv
